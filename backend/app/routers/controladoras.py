from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from psycopg import Error as DatabaseError, sql
from ..auth import administrador_escritura
from ..db import connect
from ..controladoras import META, validate, evaluate, available_options
from .recomendar import ordenar_resultados

router = APIRouter(prefix='/api', tags=['controladoras'])

class Values(BaseModel):
    model_config = ConfigDict(extra='forbid')
    cambios: dict = Field(min_length=1)

class Requirements(BaseModel):
    model_config = ConfigDict(extra='forbid')
    requisitos: dict = Field(min_length=1)
    top_n: int = Field(default=10,ge=1,le=100)

@router.get('/controladoras/campos')
def fields():
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT c.* FROM controladora_especificaciones c JOIN equipos e USING(id_equipo) WHERE e.publicado AND e.categoria='Controladora'")
            return available_options(cur.fetchall())
    except DatabaseError as exc:
        raise HTTPException(503,'No se pudieron consultar las opciones de controladoras.') from exc

@router.patch('/admin/equipos/{id_equipo}/controladora')
def edit(id_equipo: str, values: Values, _=Depends(administrador_escritura)):
    validate(values.cambios)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT categoria FROM equipos WHERE id_equipo=%s FOR UPDATE",(id_equipo,))
            row=cur.fetchone()
            if not row or row['categoria'] != 'Controladora':
                raise HTTPException(404,'Controladora no encontrada.')
            cur.execute('INSERT INTO controladora_especificaciones(id_equipo) VALUES(%s) ON CONFLICT DO NOTHING',(id_equipo,))
            # Valores se comprueban juntos para validar rangos tras una edición parcial.
            cur.execute('SELECT * FROM controladora_especificaciones WHERE id_equipo=%s',(id_equipo,))
            current = cur.fetchone(); current.pop('id_equipo')
            validate({**current,**values.cambios})
            query=sql.SQL('UPDATE controladora_especificaciones SET {} WHERE id_equipo=%s RETURNING *').format(
                sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in values.cambios))
            cur.execute(query,[*values.cambios.values(),id_equipo])
            return cur.fetchone()
    except DatabaseError as exc:
        raise HTTPException(503,'No se pudieron guardar las especificaciones de la controladora.') from exc

@router.post('/controladoras/recomendar')
def recommend(values: Requirements):
    validate(values.requisitos,requirements=True)
    selected={k:v for k,v in values.requisitos.items() if v is not None and v != '' and v is not False}
    if not selected:
        raise HTTPException(422,'Completa al menos un requisito; No significa que no se necesita.')
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.imagen_url,to_jsonb(c) AS datos FROM equipos e LEFT JOIN controladora_especificaciones c USING(id_equipo) WHERE e.publicado AND e.categoria='Controladora'")
            results=[]
            for row in cur.fetchall():
                data=row.pop('datos') or {}
                results.append({'equipo':row,**evaluate(data,selected)})
        ordenar_resultados(results)
        return {'resultados':results[:values.top_n],'total_equipos':len(results),'pesos_provisionales':True}
    except DatabaseError as exc:
        raise HTTPException(503,'No se pudo calcular el ranking de controladoras.') from exc
