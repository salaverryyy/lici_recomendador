from fastapi import FastAPI, HTTPException
from psycopg import Error as DatabaseError

from .db import connect


app = FastAPI(title="Lici Recomendador API")


@app.get("/api/equipos")
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
