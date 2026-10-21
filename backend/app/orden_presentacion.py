"""Desempates de presentación: no modifican el cumplimiento ni los puestos."""
from .comercial import precio_comparable

NOTA_ORDEN = ('En igualdad técnica se prioriza SinoGNSS; dentro de la marca, el menor costo de mercado comparable disponible y después el año más reciente. '
              'Los costos son internos; la falta de referencia no demuestra que un equipo sea más caro. '
              'Este orden no concede puntos ni acredita superioridad técnica.')


def clave_presentacion(equipo):
    year = equipo.get('anio_modelo')
    year = year if isinstance(year, int) and not isinstance(year, bool) else 0
    return (equipo.get('marca', '').casefold() != 'sinognss', precio_comparable(equipo), -year, equipo.get('id_equipo', ''))
