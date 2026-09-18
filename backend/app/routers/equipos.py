from fastapi import APIRouter, HTTPException, Query
from psycopg import Error as DatabaseError

from ..db import connect


router = APIRouter(prefix="/api/equipos", tags=["equipos"])


@router.get("")
def listar_equipos(
    q: str | None = None,
    marca: str | None = None,
    categoria: str | None = None,
    orden: str = Query(default="marca", pattern="^(marca|modelo|anio_desc|canales_desc|peso_asc)$"),
):
    orden_sql = {
        "marca": "e.marca, e.modelo",
        "modelo": "e.modelo, e.marca",
        "anio_desc": "e.anio_modelo DESC NULLS LAST, e.marca, e.modelo",
        "canales_desc": "b.canales_gnss DESC NULLS LAST, e.marca, e.modelo",
        "peso_asc": "b.peso_max ASC NULLS LAST, e.marca, e.modelo",
    }[orden]
    condiciones = ["e.publicado = TRUE"]
    parametros = []
    if q:
        condiciones.append("(e.marca ILIKE %s OR e.modelo ILIKE %s OR e.descripcion ILIKE %s)")
        parametros.extend([f"%{q}%"] * 3)
    if marca:
        condiciones.append("e.marca = %s")
        parametros.append(marca)
    if categoria:
        condiciones.append("e.categoria = %s")
        parametros.append(categoria)

    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT e.id_equipo, e.marca, e.modelo, e.categoria,
                       e.descripcion, e.imagen_url, e.anio_modelo,
                       b.tiene_imu, b.tiene_camara, b.canales_gnss,
                       b.constelaciones, b.tiene_ppp, b.peso_max
                FROM equipos AS e
                LEFT JOIN base_evaluacion AS b USING (id_equipo)
                WHERE {" AND ".join(condiciones)}
                ORDER BY {orden_sql}
                """,
                parametros,
            )
            return cur.fetchall()
    except DatabaseError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar el catálogo en PostgreSQL.",
        ) from exc


@router.get("/opciones")
def opciones_catalogo():
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT DISTINCT marca FROM equipos WHERE publicado = TRUE ORDER BY marca")
            marcas = [fila["marca"] for fila in cur.fetchall()]
            cur.execute("SELECT DISTINCT categoria FROM equipos WHERE publicado = TRUE ORDER BY categoria")
            categorias = [fila["categoria"] for fila in cur.fetchall()]
            return {"marcas": marcas, "categorias": categorias}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar las opciones del catálogo.") from exc


@router.get("/{id_equipo}")
def detalle_equipo(id_equipo: str):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM equipos WHERE id_equipo = %s AND publicado = TRUE",
                (id_equipo,),
            )
            equipo = cur.fetchone()
            if equipo is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")

            cur.execute(
                "SELECT * FROM base_evaluacion WHERE id_equipo = %s",
                (id_equipo,),
            )
            evaluacion = cur.fetchone()
            controladora = None
            if equipo['categoria'] == 'Controladora':
                cur.execute('SELECT * FROM controladora_especificaciones WHERE id_equipo=%s', (id_equipo,))
                controladora = cur.fetchone()

            cur.execute(
                """
                SELECT frecuencia_min_mhz, frecuencia_max_mhz
                FROM equipo_radio_frecuencia
                WHERE id_equipo = %s
                ORDER BY frecuencia_min_mhz, frecuencia_max_mhz
                """,
                (id_equipo,),
            )
            radio_frecuencias = cur.fetchall()
            cur.execute("SELECT id, url, texto_alternativo, orden FROM equipo_archivos WHERE id_equipo=%s AND tipo='foto' ORDER BY orden,id", (id_equipo,))
            return {
                "equipo": equipo,
                "controladora": controladora,
                "evaluacion": evaluacion,
                "radio_frecuencias": radio_frecuencias,
                "fotografias": cur.fetchall(),
            }
    except DatabaseError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar el catálogo en PostgreSQL.",
        ) from exc
