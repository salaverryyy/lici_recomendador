from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError
from ..db import connect
from ..cotecmi import es_cotecmi
from ..software import FIELDS

router = APIRouter(prefix='/api/software', tags=['software de procesamiento'])


def catalogo(solo_cotecmi=True):
    with connect() as conn, conn.cursor() as cur:
        cur.execute('SELECT * FROM software_procesamiento WHERE publicado ORDER BY marca,nombre')
        return [r for r in cur.fetchall() if not solo_cotecmi or es_cotecmi(r['marca'])]


@router.get('')
def listar(solo_cotecmi: bool = True):
    try:
        return {'software': catalogo(solo_cotecmi), 'campos': FIELDS,
                'nota': 'Software de oficina. La recomendación no acredita licencia incluida ni compatibilidad de todo el kit.'}
    except DatabaseError as exc:
        raise HTTPException(503, 'No se pudo consultar el catálogo de software.') from exc
