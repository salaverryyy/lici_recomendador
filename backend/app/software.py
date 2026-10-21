"""Software de oficina auditado. Ausencia de evidencia nunca equivale a No."""

FIELDS = {
    'estatico': 'Procesamiento estático', 'cinematico': 'Procesamiento cinemático / PPK',
    'ajuste_red': 'Ajuste de redes GNSS', 'rinex': 'Importación RINEX',
    'rinex_2': 'Importación RINEX 2.x', 'rinex_3': 'Importación RINEX 3.x',
    'informes': 'Informes de procesamiento', 'geotag': 'Georreferenciación de fotografías',
    'gratuito': 'Uso gratuito', 'windows': 'Windows', 'macos': 'macOS',
    'exporta_dxf': 'Exportación DXF', 'exporta_csv': 'Exportación CSV',
}


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
