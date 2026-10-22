"""Rangos del receptor y de sus funciones: nunca confundir cámara con láser."""
import re
import unicodedata


def _text(value):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(value).casefold()) if not unicodedata.combining(c))


def limite_operacion(datos, eje, camara=False, laser=False):
    general=datos.get(f'temperatura_operacion_{eje}_c')
    value=general
    sources=['receptor GNSS']
    for mode, active in (('camara',camara),('laser',laser)):
        limit=datos.get(f'temperatura_{mode}_{eje}_c')
        if active and limit is not None:
            sources.append('cámara' if mode=='camara' else 'láser')
            if value is not None:value=max(value,limit) if eje=='min' else min(value,limit)
    note='Se evalúa '+', '.join(sources)+'. '
    if general is not None:note+=f'Límite general del receptor: {general:g} °C. '
    if value is not None:note+=f'Límite aplicado: {value:g} °C. '
    if camara and not laser and datos.get(f'temperatura_laser_{eje}_c') is not None:
        note+='El rango propio del láser no se aplica por solicitar cámara.'
    return value,note.strip()


def respuesta_termica(message, catalog, history=None):
    query=_text(message)
    thermal_pattern=r'temperatur|rango termic|frio|calor|grados\s+(?:celsius|centigrados)|°\s*c'
    is_thermal=bool(re.search(thermal_pattern,query))
    # Un seguimiento «y el otro modelo» hereda el tema, no una conclusión previa.
    if not is_thermal and re.match(r'^\s*¿?\s*y\b',query):
        last=next((h.get('text','') for h in reversed(history or []) if h.get('role')=='user'), '')
        is_thermal=bool(re.search(thermal_pattern,_text(last)))
    if not is_thermal:return None
    rows=[]
    for row in catalog:
        if row.get('categoria')!='GNSS':continue
        model=_text(row.get('modelo',''))
        tokens=[t for t in re.findall(r'[a-z0-9]+',model) if t not in ('laser','rtk','gnss','one','plus','pro','reach','viva','portatil') and len(t)>=3]
        if model and model in query or any(re.search(r'\b'+re.escape(t)+r'\b',query) for t in tokens):rows.append(row)
    if not rows:return None
    answers=[]
    storage='almacenamiento' in query
    for row in rows:
        group='almacenamiento' if storage else 'operacion'
        low,high=(row.get(f'temperatura_{group}_{e}_c') for e in ('min','max'))
        name=f"**{row['marca']} {row['modelo']}**"
        if low is None or high is None:
            answers.append(name+f': rango de {"almacenamiento" if storage else "operación"} pendiente de confirmar.')
            continue
        parts=[f'{name}: el receptor GNSS declara **{low:g} a {high:g} °C**'+(' en almacenamiento.' if storage else ' en operación.')]
        for mode,label in (('camara','Con cámara'),('laser','Para el láser')):
            bounds=[row.get(f'temperatura_{mode}_{e}_c') for e in ('min','max')]
            if not storage and all(v is not None for v in bounds):parts.append(f'{label}, el rango específico documentado es **{bounds[0]:g} a {bounds[1]:g} °C**.')
        parts.append('La evaluación aplica las restricciones específicas solo a las funciones exigidas; no confundir operación con almacenamiento.')
        answers.append(' '.join(parts))
    return '\n\n'.join(answers)
