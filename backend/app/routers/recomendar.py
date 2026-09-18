from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError

from ..db import connect
from ..cotecmi import es_cotecmi
from ..recomendador import CRITERIOS, Preferencias, criterios_seleccionados, evaluar_equipo


router = APIRouter(prefix="/api", tags=["recomendador"])


def ordenar_resultados(resultados):
    # Compartir puesto según el porcentaje mostrado; los otros campos solo
    # mantienen un orden estable dentro del empate, no deciden un ganador.
    resultados.sort(key=lambda r: (
        -(r["porcentaje"] if r["porcentaje"] is not None else -1),
        r["sin_datos"], -r["cumplimientos"], r["equipo"]["id_equipo"],
    ))
    cantidades = {}
    for r in resultados:
        cantidades[r["porcentaje"]] = cantidades.get(r["porcentaje"], 0) + 1
    anterior = object()
    puesto = 0
    for indice, r in enumerate(resultados, 1):
        if r["porcentaje"] != anterior:
            puesto = indice
        anterior = r["porcentaje"]
        r["posicion"] = puesto
        r["empate"] = cantidades[r["porcentaje"]] > 1


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
            cur.execute("SELECT DISTINCT imu_generacion FROM base_evaluacion WHERE imu_generacion IS NOT NULL ORDER BY imu_generacion")
            generaciones = [r["imu_generacion"] for r in cur.fetchall()]
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
                "imu_generaciones": generaciones,
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
                WHERE e.publicado = TRUE AND e.categoria <> 'Controladora'
                """
            )
            equipos = [e for e in cur.fetchall() if not preferencias.solo_cotecmi or es_cotecmi(e["marca"])]
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
                if fila['id_equipo'] not in radio:
                    continue
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

        ordenar_resultados(resultados)

        return {
            "total_equipos": len(resultados),
            "top_n_solicitado": preferencias.top_n,
            "mostrados": min(preferencias.top_n, len(resultados)),
            "empate_en_primer_puesto": bool(resultados and resultados[0]["empate"]),
            "criterios_seleccionados": [criterio.clave for criterio in elegidos],
            "resultados": resultados[:preferencias.top_n],
        }
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo calcular el ranking desde PostgreSQL.") from exc
