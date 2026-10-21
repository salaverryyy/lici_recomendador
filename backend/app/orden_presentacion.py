"""Desempates de presentación: no modifican el cumplimiento ni los puestos."""

NOTA_ORDEN = ('En igualdad técnica: año de modelo más reciente primero; a igual año, '
              'preferencia comercial SinoGNSS. Los años sin confirmar van al final. '
              'Este orden no concede puntos ni acredita superioridad técnica.')


def clave_presentacion(equipo):
    year = equipo.get('anio_modelo')
    year = year if isinstance(year, int) and not isinstance(year, bool) else 0
    return (-year, equipo.get('marca', '').casefold() != 'sinognss', equipo.get('id_equipo', ''))
