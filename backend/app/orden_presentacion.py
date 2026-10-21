"""Desempates de presentación: no modifican el cumplimiento ni los puestos."""
from .comercial import precio_comparable

NOTA_ORDEN = ('En igualdad técnica: preferencia comercial SinoGNSS, luego menor precio orientativo comparable y año más reciente. '
              'Precios no disponibles: cotizar; no se consideran cero. Las referencias no son precios Cotecmi ni costos finales en Perú. '
              'Este orden no concede puntos ni acredita superioridad técnica.')


def clave_presentacion(equipo):
    year = equipo.get('anio_modelo')
    year = year if isinstance(year, int) and not isinstance(year, bool) else 0
    return (equipo.get('marca', '').casefold() != 'sinognss', precio_comparable(equipo), -year, equipo.get('id_equipo', ''))
