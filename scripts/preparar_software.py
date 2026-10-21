"""Genera la migración del catálogo auditado sin credenciales ni acceso a la BD."""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rows = json.loads((root/'docs/software/catalogo_2026-10-21.json').read_text(encoding='utf-8'))
sql = ['BEGIN;', '''CREATE TABLE IF NOT EXISTS software_procesamiento (
id_software TEXT PRIMARY KEY, marca TEXT NOT NULL, nombre TEXT NOT NULL,
descripcion TEXT NOT NULL, licencia TEXT NOT NULL, formatos TEXT NOT NULL,
funciones JSONB NOT NULL, compatibilidad TEXT NOT NULL, fuentes JSONB NOT NULL,
publicado BOOLEAN NOT NULL DEFAULT TRUE);''']
def literal(v):
    return "'" + (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict,list)) else v).replace("'", "''") + "'"
for row in rows:
    columns = list(row)
    sql.append('INSERT INTO software_procesamiento ('+','.join(columns)+') VALUES ('+','.join(literal(row[k]) for k in columns)+') ON CONFLICT(id_software) DO NOTHING;')
sql.append('COMMIT;')
(root/'sql/26_software_procesamiento.sql').write_text('\n'.join(sql)+'\n', encoding='utf-8')
