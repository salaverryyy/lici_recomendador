"""Respaldo de requisitos explícitos; no decide modelos ni inventa capacidades."""
import re
import unicodedata


def normalize(text):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c)).split())


def completar_explicitos(text, components, omitted):
    plain=normalize(text)
    gnss=components.setdefault('gnss',{})
    if re.search(r'\b4g\b|\blte\b',plain) and not re.search(r'(?:sin|no\s+(?:necesito|requiero|se exige))\s+(?:4g|lte)',plain):
        gnss['lte_4g']=True
        if re.search(r'(?:enlace|internet|conexion)\s+compartid[oa]',plain):
            gnss['lte_permite_compartido']=True
    usb=re.search(r'usb\s*[- ]?\s*(?:(?:tipo|type)\s*[- ]?\s*)?c\b',plain)
    if usb and re.search(r'carga(?:\s+de\s+energia)?',plain[max(0,usb.start()-100):usb.end()+140]) and not re.search(r'sin\s+carga|solo\s+(?:archivos|datos)',plain):
        gnss.update(usb_c=True,carga_usb_c=True)
    if re.search(r'rinex.{0,100}3\s*[.x]',plain):
        gnss.setdefault('registro_rinex_3',True)
    if re.search(r'rinex.{0,100}2\s*[.x]',plain):
        gnss.setdefault('registro_rinex_2',True)
    fall=re.search(r'(?:caida|caidas).{0,100}?(\d+(?:[.,]\d+)?)\s*metros',plain)
    if fall:
        gnss.setdefault('caida_min_m',float(fall[1].replace(',','.')))
    standard=re.search(r'mil[ -]*std[ -]*810\s*([fgh])',plain)
    if standard:
        gnss.setdefault('vibracion_norma','MIL-STD-810'+standard[1].upper())
    # El alcance común debe estar escrito, nunca deducirse por existir una colectora.
    if re.search(r'receptores\s+y\s+(?:colectoras|controladoras)',plain):
        controller=components.setdefault('controladora',{})
        for key in ('temperatura_operacion_min_c','temperatura_operacion_max_c'):
            if key in gnss:controller.setdefault(key,gnss[key])
        if 'proteccion_ip_aceptada' in gnss:
            controller['proteccion_ip']=gnss['proteccion_ip_aceptada'].replace(',',';')
        if fall:controller.setdefault('caida_m',gnss['caida_min_m'])
        if standard:omitted.append('Verificar certificado '+gnss['vibracion_norma']+' de las colectoras; la norma no tiene campo puntuable en esa familia.')
    for pattern,note in (
        (r'\bntrip\b','Verificar cliente NTRIP nativo; el acceso LTE no acredita por sí solo el protocolo.'),
        (r'webui|interfaz web','Verificar WebUI y alcance inalámbrico exigido; Wi-Fi no acredita por sí solo ambas condiciones.'),
        (r'cmr|rtcm','Verificar versiones RTCM/CMR/CMR+ y transmisión/recepción nativas, separadas de los protocolos de radio.'),
        (r'frecuencias minimas|e5a|b3\b','Verificar todas las señales/frecuencias específicas; admitir la constelación no acredita cada señal.'),
        (r'rinex.{0,100}2\s*[.x]','Verificar las revisiones RINEX exactas y señales incluidas; las familias 2.x y 3.x se evalúan por separado.'),
    ):
        if re.search(pattern,plain):omitted.append(note)
    return components
