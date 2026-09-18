"""Metadatos comunes: edición, ficha y requisitos usan las mismas unidades."""
from fastapi import HTTPException
import math
from decimal import Decimal
import re
import unicodedata

# clave, nombre, tipo, unidad, comparación del requisito
FIELDS = [
    ('sistema_operativo','Sistema operativo','text','', 'exact'),
    ('android_version','Versión Android','number','', 'min'),
    ('procesador','Procesador','text','', None),
    ('cpu_nucleos','Núcleos CPU','number','', 'min'),
    ('cpu_ghz','Frecuencia CPU','number','GHz', 'min'),
    ('ram_gb','RAM','number','GB', 'min'),
    ('almacenamiento_gb','Almacenamiento interno','number','GB', 'min'),
    ('expansion_gb','Tarjeta de expansión máxima','number','GB', 'min'),
    ('pantalla_pulgadas','Pantalla','number','pulgadas', 'min'),
    ('resolucion_ancho_px','Resolución eje corto','number','px', 'min'),
    ('resolucion_alto_px','Resolución eje largo','number','px', 'min'),
    ('brillo_nits','Brillo','number','nits', 'min'),
    ('pantalla_tactil','Pantalla táctil','boolean','', 'yes'),
    ('teclado_qwerty','Teclado QWERTY','boolean','', 'yes'),
    ('teclado_retroiluminado','Teclado retroiluminado','boolean','', 'yes'),
    ('botones_programables','Botones programables','number','', 'min'),
    ('bateria_mah','Capacidad de batería','number','mAh', 'min'),
    ('autonomia_h','Autonomía declarada mínima','number','h', 'min'),
    ('carga_h','Tiempo de carga','number','h', 'max'),
    ('carga_rapida','Carga rápida','boolean','', 'yes'),
    ('camara_mp','Cámara trasera','number','MP', 'min'),
    ('autofocus','Autoenfoque','boolean','', 'yes'),
    ('lte_4g','4G LTE','boolean','', 'yes'),
    ('bluetooth','Bluetooth','boolean','', 'yes'),
    ('bluetooth_version','Versión Bluetooth','text','', 'exact'),
    ('wifi','Wi-Fi','boolean','', 'yes'),
    ('wifi_estandar','Estándar Wi-Fi','text','', None),
    ('wifi_6','Wi-Fi 6','boolean','', 'yes'),
    ('nfc','NFC','boolean','', 'yes'),
    ('usb_c','USB-C','boolean','', 'yes'),
    ('usb_otg','USB OTG','boolean','', 'yes'),
    ('gms','Certificación Google GMS','boolean','', 'yes'),
    ('proteccion_ip','Protección IP aceptada','text','', 'exact'),
    ('temperatura_operacion_min_c','Frío de operación','number','°C', 'max'),
    ('temperatura_operacion_max_c','Calor de operación','number','°C', 'min'),
    ('temperatura_almacenamiento_min_c','Frío de almacenamiento','number','°C', 'max'),
    ('temperatura_almacenamiento_max_c','Calor de almacenamiento','number','°C', 'min'),
    ('caida_m','Caída ensayada','number','m', 'min'),
    ('peso_g','Peso con batería','number','g', 'max'),
    ('largo_mm','Largo','number','mm', 'max'),
    ('ancho_mm','Ancho','number','mm', 'max'),
    ('alto_mm','Espesor','number','mm', 'max'),
    ('bandas_celulares','Bandas celulares','text','', None),
    ('sim','Ranuras SIM','text','', None),
    ('sensores','Sensores y navegación','text','', None),
    ('software','Software y compatibilidad declarada','text','', None),
    ('notas','Condiciones y observaciones','text','', None),
    ('fuente','Ficha y versión de origen','text','', None),
]
META = {k: {'clave':k,'nombre':n,'tipo':t,'unidad':u,'modo':m} for k,n,t,u,m in FIELDS}

def canonical(key, value):
    """Unificar formatos equivalentes sin convertir especificaciones distintas."""
    if not isinstance(value, str):
        return value
    text = ' '.join(unicodedata.normalize('NFKC', value).strip().split())
    if key == 'proteccion_ip':
        compact = re.sub(r'[\s-]', '', text).upper()
        return compact if re.fullmatch(r'IP\d{2}', compact) else text.casefold()
    if key == 'bluetooth_version':
        version = re.sub(r'^(?:bluetooth|bt)\s*', '', text, flags=re.I)
        version = re.sub(r'^v(?:ersion|ersión)?\s*', '', version, flags=re.I).replace(',', '.')
        if re.fullmatch(r'\d+(?:\.\d+)?', version):
            return format(Decimal(version).normalize(), 'f') + ('.0' if '.' not in format(Decimal(version).normalize(), 'f') else '')
    if key == 'sistema_operativo' and text.casefold() in ('android', 'android os', 'sistema android'):
        return 'Android'
    return text.casefold()

def available_options(rows):
    return [{**meta, 'opciones': sorted({canonical(key, row.get(key)) for row in rows
              if row.get(key) is not None and row.get(key) != ''})}
            for key, meta in META.items()]

def validate(values, requirements=False):
    for key, value in values.items():
        if key not in META or (requirements and META[key]['modo'] is None):
            raise HTTPException(422, f'Campo no permitido: {key}')
        if value is None:
            continue
        kind = META[key]['tipo']
        valid = ((kind == 'boolean' and type(value) is bool) or
                 (kind == 'text' and type(value) is str and len(value) <= 2000) or
                 (kind == 'number' and type(value) in (int,float,Decimal) and math.isfinite(value)
                  and (value >= 0 or key.startswith('temperatura_'))))
        if not valid:
            raise HTTPException(422, f'Valor inválido para {key}')
    for prefix in ('operacion','almacenamiento'):
        lo, hi = values.get(f'temperatura_{prefix}_min_c'), values.get(f'temperatura_{prefix}_max_c')
        if not requirements and lo is not None and hi is not None and lo > hi:
            raise HTTPException(422, 'El frío no puede superar el calor del rango.')

def evaluate(data, requirements):
    detail = []
    for key, requested in requirements.items():
        if requested is None or requested == '' or requested is False:
            continue
        meta, actual = META[key], data.get(key)
        if actual is None:
            state = 'sin_datos'
        else:
            mode = meta['modo']
            meets = (actual >= requested if mode == 'min' else actual <= requested if mode == 'max'
                     else actual is True if mode == 'yes' else canonical(key, actual) == canonical(key, requested))
            state = 'cumple' if meets else 'no_cumple'
        detail.append({'clave':key,'nombre':meta['nombre'],'unidad':meta['unidad'],
                       'requerido':requested,'valor':actual,'estado':state})
    count = sum(d['estado']=='cumple' for d in detail)
    return {'porcentaje':round(100*count/len(detail),2) if detail else None,
            'cumplimientos':count,'sin_datos':sum(d['estado']=='sin_datos' for d in detail),'detalle':detail}
