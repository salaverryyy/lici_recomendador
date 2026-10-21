"""Software de oficina auditado. Ausencia de evidencia nunca equivale a No."""
import re

FIELDS = {
    'estatico': 'Procesamiento estático', 'cinematico': 'Procesamiento cinemático / PPK',
    'ajuste_red': 'Ajuste de redes GNSS', 'rinex': 'Importación RINEX',
    'rinex_2': 'Importación RINEX 2.x', 'rinex_3': 'Importación RINEX 3.x',
    'informes': 'Informes de procesamiento', 'geotag': 'Georreferenciación de fotografías',
    'gratuito': 'Uso gratuito', 'windows': 'Windows', 'macos': 'macOS',
    'exporta_dxf': 'Exportación DXF', 'exporta_csv': 'Exportación CSV',
}


def comparison_advice(message, rows, requirements, brand=None):
    """Una comparación general no convierte cantidad de documentación en calidad."""
    if not re.search(r'mejor|complet|superior|compara|diferenc|copia|copi[oó]|ex.?trabajador', message, re.I):
        return None
    names = {row['nombre'] for row in rows}
    parts = ['No hay un ganador universal: la recomendación depende del trabajo, los archivos, la licencia y el receptor. Más campos documentados no demuestran mayor calidad ni precisión.']
    if {'Compass Solution', 'PProcessing'} <= names:
        shared = [FIELDS[k] for k in ('estatico','cinematico','ajuste_red','rinex_2','rinex_3','informes','windows','exporta_dxf','exporta_csv')
                  if all(r['funciones'].get(k) is True for r in rows if r['nombre'] in ('Compass Solution','PProcessing'))]
        if shared:
            parts.append('**Compass Solution y PProcessing** comparten funciones confirmadas: '+', '.join(shared)+'. Eso no acredita idéntico rendimiento. Revisa los límites de versión y formato en sus fichas, especialmente los datos dinámicos ComNav y el dongle documentados para Compass V2.0.1.')
    if brand in ('SinoGNSS','SingularXYZ','Emlid'):
        native = {'SinoGNSS':'Compass Solution','SingularXYZ':'PProcessing','Emlid':'Emlid Studio'}[brand]
        parts.append(f'Para el receptor {brand} seleccionado, prioriza **{native}** por su ecosistema, sujeto a comprobar archivos y licencia.')
    else:
        parts.append('Para un receptor **SinoGNSS**, la primera opción del ecosistema es **Compass Solution**; para SingularXYZ, PProcessing; para Emlid, Emlid Studio. Esto no concede superioridad técnica por marca.')
    if 'Emlid Studio' in names:
        parts.append('**Emlid Studio** ofrece procesamiento estático/PPK, geotag y uso gratuito; su gratuidad no significa que su PPK sea básico. El ajuste de redes sigue pendiente de confirmar.')
    if requirements:
        parts.append('Los porcentajes de abajo miden únicamente los requisitos explícitos evaluados; un empate no permite declarar un software superior.')
    else:
        parts.append('Indica si necesitas ajuste de redes, PPK de drones, un sistema operativo o un formato concreto para afinar la elección.')
    if re.search(r'copia|copi[oó]|ex.?trabajador', message, re.I):
        parts.append('Las fuentes técnicas revisadas no acreditan la afirmación sobre copias u origen empresarial; no se utiliza para puntuar.')
    return ' '.join(parts)


def validate(requirements):
    if not isinstance(requirements, dict) or len(requirements) > len(FIELDS):
        raise ValueError('Requisitos de software inválidos')
    if any(k not in FIELDS or not isinstance(v, bool) for k, v in requirements.items()):
        raise ValueError('Usa funciones de software permitidas y valores booleanos')
    return {k: v for k, v in requirements.items() if v}


def rank(rows, requirements, marca=None, misma_marca=False):
    requirements = validate(requirements)
    results = []
    for row in rows:
        same = bool(marca and row['marca'].casefold() == marca.casefold())
        if misma_marca and marca and not same:
            continue
        details = [{'clave': k, 'nombre': FIELDS[k], 'pedido': True,
                    'valor_equipo': row['funciones'].get(k),
                    'estado': 'cumple' if row['funciones'].get(k) is True else
                              'incumple' if row['funciones'].get(k) is False else 'sin_datos'}
                   for k in requirements]
        met = sum(d['estado'] == 'cumple' for d in details)
        results.append({'software': row, 'misma_marca_gnss': same, 'detalle': details,
                        'porcentaje': round(100*met/len(details), 2) if details else None,
                        'incumplimientos': sum(d['estado'] == 'incumple' for d in details),
                        'sin_datos': sum(d['estado'] == 'sin_datos' for d in details)})
    # La relación de marca no concede puntos de cumplimiento técnico.
    results.sort(key=lambda r: (-(r['porcentaje'] if r['porcentaje'] is not None else -1),
                                not r['misma_marca_gnss'], r['software']['nombre']))
    return {'resultados': results, 'total_equipos': len(results),
            'criterios': requirements, 'metodo': 'cumplimiento_binario'}
