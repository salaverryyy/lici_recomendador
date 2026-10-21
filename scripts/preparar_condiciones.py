"""Genera la migración incremental LTE/SIM y configuraciones confirmadas."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'docs/comercial/lte_sim_2026-10-21.json').read_text(encoding='utf-8'))
def lit(value):
    if value is None:return 'NULL'
    if isinstance(value,bool):return 'TRUE' if value else 'FALSE'
    return "'"+str(value).replace("'","''")+"'"
sql=['BEGIN;']
for table in ('base_evaluacion','controladora_especificaciones','slam_especificaciones'):
    sql += [f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS sim_fisica BOOLEAN;',f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS conectividad_nota TEXT;']
sql += ['ALTER TABLE slam_especificaciones ADD COLUMN IF NOT EXISTS lte_4g BOOLEAN;',
        'ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS memoria_interna_opcional_max_gb NUMERIC;',
        'ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS memoria_interna_opciones_gb JSONB;',
        'ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS usb_c_con_adaptador BOOLEAN;']
for row in rows:
    sql.append(f"UPDATE {row['tabla']} SET lte_4g={lit(row['lte_4g'])},sim_fisica={lit(row['sim_fisica'])},conectividad_nota={lit(row['nota'])} WHERE id_equipo={lit(row['id_equipo'])};")
    if row['tabla']=='base_evaluacion':
        combined=row['lte_4g'] and row['sim_fisica'] if row['lte_4g'] is not None else None
        sql.append(f"UPDATE base_evaluacion SET sim_4g={lit(combined)} WHERE id_equipo={lit(row['id_equipo'])};")
    # La auditoría guarda alcance y procedencia sin presentar declaraciones
    # comerciales como si fueran una ficha del fabricante.
    for field in ('lte_4g','sim_fisica'):
        value=row[field]
        sql.append("INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) VALUES ("+','.join(lit(v) for v in (row['id_equipo'],field,str(value) if value is not None else 'Pendiente de confirmar',row['fuente_url'] or 'https://licitex-omega.vercel.app/',row.get('documento') or 'Revisión de documentación del modelo','condiciones-2026-10-21','confirmado' if value is not None else 'no_verificado',row['nota']))+") ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;")
    if row.get('memoria_interna_opciones_gb'):
        sql.append(f"UPDATE base_evaluacion SET memoria_interna_opcional_max_gb={row['memoria_interna_opcional_max_gb']},memoria_interna_opciones_gb={lit(json.dumps(row['memoria_interna_opciones_gb']))}::jsonb WHERE id_equipo={lit(row['id_equipo'])};")
sql += ["UPDATE base_evaluacion SET memoria_opcional_fabrica_max_gb=32 WHERE id_equipo='GNSS-SINOGNSS-JUPITER';",
        # Declaración comercial Cotecmi: no cambia el conector nativo del fabricante.
        "UPDATE base_evaluacion SET usb_c_con_adaptador=TRUE WHERE lemo=TRUE AND lemo_pines=7;"]
sql.append('COMMIT;')
(root/'sql/28_condiciones_sim.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
