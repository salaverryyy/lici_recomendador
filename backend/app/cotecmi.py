"""Marcas comercializadas por Cotecmi, según el catálogo del usuario."""
COTECMI_MARCAS = ('SingularXYZ', 'SinoGNSS', 'Emlid')


def es_cotecmi(marca: str) -> bool:
    return marca.strip().casefold() in {m.casefold() for m in COTECMI_MARCAS}
