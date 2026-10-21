"""Referencias comerciales independientes de las especificaciones del fabricante."""
from pathlib import Path
import json
from functools import lru_cache

PATH=Path(__file__).resolve().parents[2]/'docs/comercial/referencias_2026-10-21.json'


@lru_cache(maxsize=1)
def referencias():
    return {r['id_equipo']:r for r in json.loads(PATH.read_text(encoding='utf-8'))}


def referencia(ident):
    return referencias().get(ident)


def enriquecer(equipo):
    return {**equipo,'referencia_precio':referencia(equipo['id_equipo'])}


def precio_comparable(equipo):
    reference=equipo.get('referencia_precio') or {}
    value=reference.get('precio_usd')
    return float(value) if reference.get('comparable') and isinstance(value,(int,float)) and value>0 else float('inf')


def sin_precios(value):
    """Las referencias comerciales se usan en el servidor, nunca en respuestas públicas."""
    if isinstance(value, dict):
        return {key: sin_precios(item) for key, item in value.items() if key != 'referencia_precio'}
    if isinstance(value, (list, tuple)):
        return [sin_precios(item) for item in value]
    return value
