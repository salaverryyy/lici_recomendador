from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError

from ..db import connect


router = APIRouter(prefix="/api/equipos", tags=["equipos"])


@router.get("")
def listar_equipos():
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.id_equipo, e.marca, e.modelo, e.categoria,
                       e.descripcion, e.imagen_url,
                       b.tiene_imu, b.tiene_camara, b.canales_gnss,
                       b.constelaciones, b.tiene_ppp
                FROM equipos AS e
                LEFT JOIN base_evaluacion AS b USING (id_equipo)
                WHERE e.publicado = TRUE
                ORDER BY e.marca, e.modelo
                """
            )
            return cur.fetchall()
    except DatabaseError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar el catálogo en PostgreSQL.",
        ) from exc


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

            cur.execute(
                """
                SELECT frecuencia_min_mhz, frecuencia_max_mhz
                FROM equipo_radio_frecuencia
                WHERE id_equipo = %s
                ORDER BY frecuencia_min_mhz, frecuencia_max_mhz
                """,
                (id_equipo,),
            )
            return {
                "equipo": equipo,
                "evaluacion": evaluacion,
                "radio_frecuencias": cur.fetchall(),
            }
    except DatabaseError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar el catálogo en PostgreSQL.",
        ) from exc
