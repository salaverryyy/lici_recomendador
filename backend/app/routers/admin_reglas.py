from fastapi import APIRouter, Depends, HTTPException
from psycopg import Error as DatabaseError
from pydantic import BaseModel, ConfigDict, Field

from ..auth import administrador_actual, administrador_escritura
from ..db import connect
from ..recomendador import CRITERIOS, CRITERIOS_POR_CLAVE
from .recomendar import leer_reglas


router = APIRouter(prefix="/api/admin/reglas", tags=["administración: reglas"])


class ReglaEditable(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    peso: float = Field(ge=0, le=1000)
    activo: bool = True


class ReglaConClave(ReglaEditable):
    criterio: str


@router.get("")
def ver_reglas(_=Depends(administrador_actual)):
    try:
        with connect() as conn, conn.cursor() as cur:
            pesos, activos = leer_reglas(cur)
            return [
                {
                    "criterio": criterio.clave,
                    "nombre": criterio.nombre,
                    "peso": pesos[criterio.clave],
                    "activo": activos[criterio.clave],
                }
                for criterio in CRITERIOS
            ]
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar las reglas.") from exc


@router.put("/{criterio}")
def editar_regla(criterio: str, datos: ReglaEditable, _=Depends(administrador_escritura)):
    if criterio not in CRITERIOS_POR_CLAVE:
        raise HTTPException(status_code=404, detail="Criterio no reconocido.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reglas_recomendacion (criterio, peso, activo)
                VALUES (%s, %s, %s)
                ON CONFLICT (criterio) DO UPDATE
                SET peso = EXCLUDED.peso, activo = EXCLUDED.activo
                RETURNING criterio, peso, activo
                """,
                (criterio, datos.peso, datos.activo),
            )
            return cur.fetchone()
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo editar la regla.") from exc


@router.put("")
def editar_reglas(reglas: list[ReglaConClave], _=Depends(administrador_escritura)):
    if not reglas or len(reglas) > len(CRITERIOS):
        raise HTTPException(status_code=422, detail="Envía entre 1 y 23 reglas.")
    claves = [regla.criterio for regla in reglas]
    if len(set(claves)) != len(claves) or any(clave not in CRITERIOS_POR_CLAVE for clave in claves):
        raise HTTPException(status_code=422, detail="Hay criterios repetidos o desconocidos.")
    try:
        with connect() as conn, conn.cursor() as cur:
            for regla in reglas:
                cur.execute(
                    """
                    INSERT INTO reglas_recomendacion (criterio, peso, activo)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (criterio) DO UPDATE
                    SET peso = EXCLUDED.peso, activo = EXCLUDED.activo
                    """,
                    (regla.criterio, regla.peso, regla.activo),
                )
            return {"reglas_actualizadas": len(reglas)}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo editar las reglas.") from exc
