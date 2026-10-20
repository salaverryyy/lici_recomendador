from fastapi import APIRouter, Depends, HTTPException
from psycopg import Error as DatabaseError, sql
from pydantic import BaseModel, ConfigDict, Field

from ..auth import administrador_escritura
from ..cotecmi import es_cotecmi
from ..db import connect
from ..slam import META, available_options, evaluate, validate
from .recomendar import ordenar_resultados, limitar_con_empates


router = APIRouter(prefix="/api", tags=["escáneres SLAM"])


class Values(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cambios: dict = Field(min_length=1)


class Requirements(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requisitos: dict = Field(min_length=1)
    solo_cotecmi: bool = False
    top_n: int = Field(default=10, ge=1, le=100)


@router.get("/slam/campos")
def fields():
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT s.* FROM slam_especificaciones s
                JOIN equipos e USING(id_equipo)
                WHERE e.publicado AND e.categoria='Escáner SLAM'
            """)
            return available_options(cur.fetchall())
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudieron consultar las opciones SLAM.") from exc


@router.patch("/admin/equipos/{id_equipo}/slam")
def edit(id_equipo: str, values: Values, _=Depends(administrador_escritura)):
    validate(values.cambios)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT categoria FROM equipos WHERE id_equipo=%s FOR UPDATE", (id_equipo,))
            row = cur.fetchone()
            if not row or row["categoria"] != "Escáner SLAM":
                raise HTTPException(404, "Escáner SLAM no encontrado.")
            cur.execute("INSERT INTO slam_especificaciones(id_equipo) VALUES(%s) ON CONFLICT DO NOTHING", (id_equipo,))
            cur.execute("SELECT * FROM slam_especificaciones WHERE id_equipo=%s", (id_equipo,))
            current = cur.fetchone()
            current.pop("id_equipo")
            validate({**current, **values.cambios})
            query = sql.SQL("UPDATE slam_especificaciones SET {} WHERE id_equipo=%s RETURNING *").format(
                sql.SQL(",").join(sql.SQL("{}=%s").format(sql.Identifier(key)) for key in values.cambios)
            )
            cur.execute(query, [*values.cambios.values(), id_equipo])
            return cur.fetchone()
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudieron guardar las especificaciones SLAM.") from exc


@router.post("/slam/recomendar")
def recommend(values: Requirements):
    validate(values.requisitos, requirements=True)
    selected = {
        key: value for key, value in values.requisitos.items()
        if value is not None and value != "" and value is not False
    }
    if not selected:
        raise HTTPException(422, "Completa al menos un requisito; No significa que no se necesita.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.imagen_url,to_jsonb(s) AS datos
                FROM equipos e LEFT JOIN slam_especificaciones s USING(id_equipo)
                WHERE e.publicado AND e.categoria='Escáner SLAM'
            """)
            results = []
            for row in cur.fetchall():
                if values.solo_cotecmi and not es_cotecmi(row["marca"]):
                    continue
                data = row.pop("datos") or {}
                results.append({"equipo": row, **evaluate(data, selected)})
        ordenar_resultados(results)
        return {
            "resultados": limitar_con_empates(results, values.top_n),
            "mostrados": len(limitar_con_empates(results, values.top_n)),
            "total_equipos": len(results),
            "pesos_provisionales": True,
        }
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo calcular el ranking de escáneres SLAM.") from exc
