"""Etiquetas de evidencia: nunca reemplazan valores técnicos usados para puntuar."""

def etiquetas_auditoria(cur, ids):
    cur.execute("""
        SELECT DISTINCT ON (id_equipo,campo) id_equipo,campo,valor_declarado,estado,
               fuente_url,documento,nota,fecha_consulta
        FROM equipo_dato_fuentes WHERE id_equipo=ANY(%s)
        ORDER BY id_equipo,campo,fecha_consulta DESC,id DESC
    """, (ids,))
    result = {ident: {} for ident in ids}
    for row in cur.fetchall():
        row['etiqueta'] = etiqueta_sin_valor({row['campo']:row},row['campo'])
        result[row['id_equipo']][row['campo']] = row
    return result


def etiqueta_sin_valor(auditoria, campo):
    row = auditoria.get(campo) or {}
    value = row.get('valor_declarado', '')
    if value in ('No aplica', 'Depende del kit ofertado', 'Modo no especificado por separado', 'Sin límite angular impuesto'):
        return value
    return 'No publicado / pendiente de confirmar'
