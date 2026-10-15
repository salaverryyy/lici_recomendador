"""Metadatos, validación y evaluación de escáneres LiDAR con SLAM."""

import math
import re
import unicodedata
from decimal import Decimal

from fastapi import HTTPException


# clave, nombre, tipo, unidad, comparación del requisito
FIELDS = [
    ("aplicaciones", "Aplicación principal", "text", "", "contains"),
    ("tecnologia_slam", "Tecnología SLAM", "text", "", None),
    ("lineas_lidar", "Canales LiDAR", "number", "líneas", "min"),
    ("laser_clase_1", "Láser Clase 1 seguro para la vista", "boolean", "", "yes"),
    ("longitud_onda_nm", "Longitud de onda", "number", "nm", None),
    ("alcance_lidar_m", "Alcance LiDAR", "number", "m", "min"),
    ("puntos_por_segundo", "Velocidad de adquisición", "number", "puntos/s", "min"),
    ("fov_horizontal_deg", "Campo de visión horizontal", "number", "°", "min"),
    ("fov_vertical_deg", "Campo de visión vertical", "number", "°", "min"),
    ("precision_nube_cm", "Precisión de nube de puntos", "number", "cm", "max"),
    ("gnss_disponible", "Georreferenciación mediante GNSS", "boolean", "", "yes"),
    ("gnss_integrado", "GNSS integrado", "boolean", "", "yes"),
    ("gnss_opcional", "GNSS mediante módulo o accesorio", "boolean", "", "yes"),
    ("rtk_disponible", "RTK disponible", "boolean", "", "yes"),
    ("operacion_sin_gnss", "Operación SLAM sin señal GNSS", "boolean", "", "yes"),
    ("tiene_imu", "IMU", "boolean", "", "yes"),
    ("cantidad_camaras", "Cantidad de cámaras", "number", "", "min"),
    ("resolucion_camara_mp", "Resolución de cámara", "number", "MP", "min"),
    ("colorizacion_rgb", "Colorización RGB", "boolean", "", "yes"),
    ("visualizacion_tiempo_real", "Visualización en tiempo real", "boolean", "", "yes"),
    ("peso_operativo_g", "Peso de configuración manual", "number", "g", "max"),
    ("autonomia_h", "Autonomía continua por batería", "number", "h", "min"),
    ("baterias_incluidas", "Baterías declaradas", "number", "", "min"),
    ("hot_swap", "Cambio de batería en caliente", "boolean", "", "yes"),
    ("proteccion_ip", "Protección IP mínima", "text", "", "ip"),
    ("temperatura_operacion_min_c", "Frío de operación", "number", "°C", "max"),
    ("temperatura_operacion_max_c", "Calor de operación", "number", "°C", "min"),
    ("almacenamiento_gb", "Almacenamiento interno", "number", "GB", "min"),
    ("almacenamiento_expandible", "Almacenamiento ampliable por el usuario", "boolean", "", "yes"),
    ("usb_c", "USB-C", "boolean", "", "yes"),
    ("wifi", "Wi-Fi", "boolean", "", "yes"),
    ("bluetooth", "Bluetooth", "boolean", "", "yes"),
    ("software_adquisicion_incluido", "Software de adquisición incluido", "boolean", "", "yes"),
    ("software_postproceso_incluido", "Software de postproceso incluido", "boolean", "", "yes"),
    ("exporta_las", "Exportación LAS", "boolean", "", "yes"),
    ("exporta_laz", "Exportación LAZ", "boolean", "", "yes"),
    ("exporta_e57", "Exportación E57", "boolean", "", "yes"),
    ("exporta_ply", "Exportación PLY", "boolean", "", "yes"),
    ("exporta_dxf", "Exportación DXF", "boolean", "", "yes"),
    ("formatos_salida", "Formatos de salida declarados", "text", "", None),
    ("modos_montaje", "Modos de uso y montaje", "text", "", None),
    ("software", "Software y funciones declaradas", "text", "", None),
    ("notas", "Condiciones y observaciones", "text", "", None),
    ("fuente", "Ficha y versión de origen", "text", "", None),
]

META = {
    key: {"clave": key, "nombre": name, "tipo": kind, "unidad": unit, "modo": mode}
    for key, name, kind, unit, mode in FIELDS
}

TENDER_OPTIONS = {
    "aplicaciones": [
        "Interiores", "Exteriores", "Topografía", "Minería", "Infraestructura",
        "Modelado 3D", "Emergencias", "Agricultura y forestal", "Plataformas móviles",
    ],
    "lineas_lidar": [16, 32, 40],
    "alcance_lidar_m": [70, 120, 300],
    "puntos_por_segundo": [200_000, 320_000, 480_000, 640_000],
    "fov_horizontal_deg": [360],
    "precision_nube_cm": [1, 2, 3],
    "autonomia_h": [2],
    "almacenamiento_gb": [256, 512, 1024],
    "peso_operativo_g": [1500],
    "proteccion_ip": ["IP54", "IP64", "IP65"],
}

INTEGER_FIELDS = {
    "lineas_lidar",
    "puntos_por_segundo",
    "cantidad_camaras",
    "baterias_incluidas",
}


def canonical(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char)).strip()


def available_options(rows: list[dict]) -> list[dict]:
    result = []
    for key, meta in META.items():
        values = set(TENDER_OPTIONS.get(key, []))
        for row in rows:
            value = row.get(key)
            if value is None or value == "":
                continue
            if meta["modo"] == "contains":
                values.update(item.strip() for item in str(value).split(";") if item.strip())
            else:
                values.add(value)
        result.append({**meta, "opciones": sorted(values, key=lambda item: (str(type(item)), str(item)))})
    return result


def validate(values: dict, requirements: bool = False):
    for key, value in values.items():
        if key not in META or (requirements and META[key]["modo"] is None):
            raise HTTPException(422, f"Campo SLAM no permitido: {key}")
        if value is None:
            continue
        kind = META[key]["tipo"]
        valid = (
            (kind == "boolean" and type(value) is bool)
            or (kind == "text" and isinstance(value, str) and len(value) <= 4000)
            or (
                kind == "number"
                and type(value) in (int, float, Decimal)
                and math.isfinite(value)
                and (key not in INTEGER_FIELDS or int(value) == value)
                and (value >= 0 or key.startswith("temperatura_"))
            )
        )
        if not valid:
            raise HTTPException(422, f"Valor inválido para {key}")
        if key == "proteccion_ip" and value and not re.fullmatch(r"IP[0-6][0-9]", value.upper()):
            raise HTTPException(422, "Usa un código IP como IP54 o IP65.")
    lo = values.get("temperatura_operacion_min_c")
    hi = values.get("temperatura_operacion_max_c")
    if not requirements and lo is not None and hi is not None and lo > hi:
        raise HTTPException(422, "La temperatura mínima no puede superar la máxima.")


def _ip_meets(actual: str, requested: str) -> bool:
    actual_match = re.fullmatch(r"IP([0-6])([0-9])", actual.upper())
    requested_match = re.fullmatch(r"IP([0-6])([0-9])", requested.upper())
    return bool(
        actual_match
        and requested_match
        and int(actual_match.group(1)) >= int(requested_match.group(1))
        and int(actual_match.group(2)) >= int(requested_match.group(2))
    )


def evaluate(data: dict, requirements: dict) -> dict:
    detail = []
    for key, requested in requirements.items():
        if requested is None or requested == "" or requested is False:
            continue
        meta = META[key]
        actual = data.get(key)
        if actual is None:
            state = "sin_datos"
        else:
            mode = meta["modo"]
            if mode == "min":
                meets = actual >= requested
            elif mode == "max":
                meets = actual <= requested
            elif mode == "yes":
                meets = actual is True
            elif mode == "ip":
                meets = _ip_meets(str(actual), str(requested))
            elif mode == "contains":
                options = {canonical(item) for item in str(actual).split(";")}
                meets = canonical(requested) in options
            else:
                meets = canonical(actual) == canonical(requested)
            state = "cumple" if meets else "no_cumple"
        detail.append({
            "clave": key, "nombre": meta["nombre"], "unidad": meta["unidad"],
            "requerido": requested, "valor": actual, "estado": state,
        })
    count = sum(item["estado"] == "cumple" for item in detail)
    return {
        "porcentaje": round(100 * count / len(detail), 2) if detail else None,
        "cumplimientos": count,
        "sin_datos": sum(item["estado"] == "sin_datos" for item in detail),
        "detalle": detail,
    }
