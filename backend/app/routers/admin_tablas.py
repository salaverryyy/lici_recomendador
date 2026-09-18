from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import sql, Error as DatabaseError
from ..auth import administrador_actual
from ..db import connect

router = APIRouter(prefix="/api/admin/tablas", tags=["administración: tablas"])
TABLAS = {"equipos": "id_equipo", "base_evaluacion": "id_equipo",
          "equipo_radio_frecuencia": "id", "equipo_archivos": "id",
          "reglas_recomendacion": "criterio", "controladora_especificaciones": "id_equipo"}


@router.get("")
def listar(_=Depends(administrador_actual)):
    return {"tablas": list(TABLAS)}


@router.get("/{tabla}")
def consultar(tabla: str, pagina: int = Query(default=1, ge=1),
              limite: int = Query(default=25, ge=1, le=100),
              _=Depends(administrador_actual)):
    if tabla not in TABLAS:
        raise HTTPException(404, "Tabla no disponible.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT count(*) AS total FROM {}").format(sql.Identifier(tabla)))
            total = cur.fetchone()["total"]
            cur.execute(sql.SQL("SELECT * FROM {} ORDER BY {} LIMIT %s OFFSET %s").format(
                sql.Identifier(tabla), sql.Identifier(TABLAS[tabla])),
                (limite, (pagina - 1) * limite))
            filas = cur.fetchall()
            columnas = [c.name for c in cur.description]
            return {"tabla": tabla, "columnas": columnas, "filas": filas,
                    "total": total, "pagina": pagina, "limite": limite}
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo consultar la tabla.") from exc
