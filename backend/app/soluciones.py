"""Compone opciones de oficina/campo sin convertir afinidad de marca en compatibilidad."""
from .software import rank as rank_software


def unscored(row):
    return {'equipo': {k: row.get(k) for k in ('id_equipo','marca','modelo','categoria')},
            'porcentaje': None, 'detalle': [], 'sin_datos': 0}


def issues(result):
    details = (result or {}).get('detalle', [])
    return (sum(d['estado'] in ('incumple','no_cumple') for d in details),
            sum(d['estado']=='sin_datos' for d in details))


def assemble(gnss, controllers, software, requirements, selections, reference=None, strict=False, limit=20):
    anchor = selections.get('gnss') or reference
    if anchor:
        gnss = [r for r in gnss if r['equipo']['id_equipo']==anchor]
    if selections.get('controladora'):
        controllers = [r for r in controllers if r['equipo']['id_equipo']==selections['controladora']]
    if selections.get('software'):
        software = [r for r in software if r['id_software']==selections['software']]
    options = []
    for receiver in gnss:
        brand = receiver['equipo']['marca']
        candidates = [r for r in controllers if not strict or r['equipo']['marca']==brand]
        candidates.sort(key=lambda r: (issues(r)[0], -(r.get('porcentaje') or 0), issues(r)[1], r['equipo']['marca']!=brand, r['equipo']['id_equipo']))
        controller = candidates[0] if candidates else None
        native = [r for r in software if r['marca']==brand]
        # No se presume intercambiabilidad de formatos entre todas las marcas.
        software_rank = rank_software(native, requirements.get('software', {}), brand, True)
        processing = next(iter(software_rank['resultados']), None)
        configured = [r for r in (receiver, controller, processing) if r and r.get('porcentaje') is not None]
        score = round(sum(r['porcentaje'] for r in configured)/len(configured), 2) if configured else None
        failures = sum(issues(r)[0] for r in (receiver, controller, processing))
        unknown = sum(issues(r)[1] for r in (receiver, controller, processing))
        pending = ['Validar app de campo, versión, enlace receptor–controladora, formatos y licencia de oficina con el proveedor.']
        if not controller:
            pending.append('No hay controladora publicada que respete la selección/condición de marca.')
        elif controller['equipo']['marca']!=brand:
            pending.append('Controladora de otra marca: compatibilidad pendiente, no acreditada por tener Bluetooth o Android.')
        if not processing:
            pending.append('No hay software auditado de esta marca que respete la selección. No se sustituye automáticamente por software de otra marca.')
        if requirements.get('gnss', {}).get('memoria_min_gb') or processing:
            pending.append('Verificar registro de observaciones brutas del receptor y un archivo de prueba base/rover.')
        not_evaluated = [family for family in ('gnss','controladora','software') if not requirements.get(family)]
        options.append({'gnss': receiver, 'controladora': controller, 'software': processing,
                        'alternativas_controladora': [r['equipo'] for r in candidates[1:]],
                        'porcentaje': score, 'incumplimientos': failures, 'sin_datos': unknown,
                        'estado': 'no_cumple' if failures or (strict and (not controller or not processing)) else 'pendiente_validacion',
                        'pendientes': pending, 'familias_sin_requisitos': not_evaluated,
                        'seleccion_explicita': bool(selections.get('gnss'))})
    options.sort(key=lambda o: (o['estado']=='no_cumple', -(o['porcentaje'] if o['porcentaje'] is not None else -1), o['sin_datos'], o['gnss']['equipo']['id_equipo']))
    shown = options[:limit]
    if shown:
        boundary = (shown[-1]['estado'], shown[-1]['porcentaje'])
        shown.extend(o for o in options[limit:] if (o['estado'],o['porcentaje'])==boundary)
    return {'opciones': shown, 'total': len(options), 'misma_marca_exigida': strict,
            'nota': 'Orden GNSS → controladora → software de oficina. Porcentaje parcial: media por familia con requisitos; no acredita cumplimiento total ni compatibilidad del conjunto. Los incumplimientos conocidos se muestran después de las opciones sin incumplimientos.'}
