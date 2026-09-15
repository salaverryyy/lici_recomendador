from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError

from ..db import connect
from ..recomendador import CRITERIOS, Preferencias, criterios_seleccionados, evaluar_equipo


router = APIRouter(prefix="/api", tags=["recomendador"])


def leer_reglas(cur):
    pesos = {criterio.clave: criterio.peso for criterio in CRITERIOS}
    activos = {criterio.clave: True for criterio in CRITERIOS}
    cur.execute("SELECT criterio, peso, activo FROM reglas_recomendacion")
    for fila in cur.fetchall():
        if fila["criterio"] in pesos:
            pesos[fila["criterio"]] = float(fila["peso"])
            activos[fila["criterio"]] = fila["activo"]
    return pesos, activos


@router.get("/recomendador/criterios")
def ver_criterios():
    try:
        with connect() as conn, conn.cursor() as cur:
            pesos, activos = leer_reglas(cur)
            return {
                "criterios": [
                    {
                        "clave": criterio.clave,
                        "campo_input": criterio.campo_input,
                        "nombre": criterio.nombre,
                        "unidad": criterio.unidad,
                        "modo": criterio.modo,
                        "peso": pesos[criterio.clave],
                        "activo": activos[criterio.clave],
                    }
                    for criterio in CRITERIOS
                ],
                "pesos_provisionales": True,
                "booleano_no": "No significa que no se necesita; no aporta puntos ni peso.",
            }
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar las reglas en PostgreSQL.") from exc


@router.post("/recomendar")
def recomendar(preferencias: Preferencias):
    elegidos = criterios_seleccionados(preferencias)
    if not elegidos:
        raise HTTPException(status_code=422, detail="Selecciona al menos un criterio; los booleanos en No no cuentan.")

    try:
        with connect() as conn, conn.cursor() as cur:
            pesos, activos = leer_reglas(cur)
            desactivados = [criterio.clave for criterio in elegidos if not activos[criterio.clave]]
            if desactivados:
                raise HTTPException(status_code=422, detail={"criterios_inactivos": desactivados})

            cur.execute(
                """
                SELECT e.id_equipo, e.marca, e.modelo, e.categoria, e.imagen_url,
                       to_jsonb(b) AS evaluacion
                FROM equipos AS e
                LEFT JOIN base_evaluacion AS b USING (id_equipo)
                WHERE e.publicado = TRUE
                """
            )
            equipos = cur.fetchall()
            cur.execute(
                """
                SELECT r.id_equipo, r.frecuencia_min_mhz, r.frecuencia_max_mhz
                FROM equipo_radio_frecuencia AS r
                JOIN equipos AS e USING (id_equipo)
                WHERE e.publicado = TRUE
                """
            )
            radio = {equipo["id_equipo"]: [] for equipo in equipos}
            for fila in cur.fetchall():
                radio[fila["id_equipo"]].append({
                    "min_mhz": fila["frecuencia_min_mhz"],
                    "max_mhz": fila["frecuencia_max_mhz"],
                })

        resultados = []
        for equipo in equipos:
            puntuacion = evaluar_equipo(
                preferencias,
                elegidos,
                pesos,
                equipo["evaluacion"],
                radio[equipo["id_equipo"]],
            )
            resultados.append({
                "equipo": {
                    "id_equipo": equipo["id_equipo"],
                    "marca": equipo["marca"],
                    "modelo": equipo["modelo"],
                    "categoria": equipo["categoria"],
                    "imagen_url": equipo["imagen_url"],
                },
                **puntuacion,
            })

        resultados.sort(key=lambda resultado: (
            -(resultado["porcentaje"] if resultado["porcentaje"] is not None else -1),
            resultado["sin_datos"],
            -resultado["cumplimientos"],
            resultado["equipo"]["id_equipo"],
        ))
        for posicion, resultado in enumerate(resultados, start=1):
            resultado["posicion"] = posicion

        return {
            "total_equipos": len(resultados),
            "top_n_solicitado": preferencias.top_n,
            "mostrados": min(preferencias.top_n, len(resultados)),
            "criterios_seleccionados": [criterio.clave for criterio in elegidos],
            "resultados": resultados[:preferencias.top_n],
        }
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo calcular el ranking desde PostgreSQL.") from exc
