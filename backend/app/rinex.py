"""Separar formato compatible, registro en receptor y conversión de observaciones."""


def capacidad_rinex(data, version, native=False):
    direct=data.get(f'rinex_{version}_directo')
    conversion=data.get(f'rinex_{version}_conversion')
    software=data.get('rinex_conversion_software')
    note=data.get('rinex_conversion_nota') or ''
    if native:
        return direct, False, ('Se exige generación directa en el receptor; convertir en oficina no cubre esta condición. '+note).strip()
    if direct is True:
        return True, False, ('Registro/exportación directa documentada para RINEX '+version+'.x. '+note).strip()
    if conversion is True:
        return True, True, ('Cumple mediante conversión de observaciones brutas con '+(software or 'software documentado')+'. Verificar versión, archivo de entrada y disponibilidad/licencia; no se presume software incluido. '+note).strip()
    value=data.get('registro_rinex_'+version)
    if value is None and direct is False and conversion is False:value=False
    return value, False, ('La compatibilidad publicada no acredita todas las revisiones ni un registro directo. '+note).strip()
