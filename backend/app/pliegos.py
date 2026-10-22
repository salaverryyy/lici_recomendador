"""Lectura estable de cláusulas explícitas, sin consultar datos de candidatos.

Se usa como base de pliegos extensos estructurados. Las cláusulas fuera de esta
gramática quedan para revisión, nunca se completan con el estándar del catálogo.
"""
import re
from .cobertura_texto import normalize, completar_explicitos


def extraer_pliego(text):
    if re.search(r'(?:^|\n)\s*[¿?]?\s*(?:por qu[eé]|porque|explica|compara)\b', text, re.I):
        return None
    plain = normalize(text)
    gnss = {}
    def number(pattern, key, scale=1):
        match = re.search(pattern, plain)
        if match:
            gnss[key] = float(match[1].replace(',', '.')) * scale
    n = r'(\d+(?:[.,]\d+)?)'
    number(r'(?:capacidad minima de|minimo de|al menos)\s*'+n+r'\s*canales', 'canales_min')
    constellations = re.search(r'constelaciones soportadas\s*:(.*?)(?:frecuencias|precision|\n|$)', plain)
    if constellations:
        for name in ('gps','glonass','galileo','beidou','qzss','sbas'):
            if re.search(r'\b'+name+r'\b', constellations[1]):gnss[name] = True
    for mode, heading in (('rtk',r'precision en tiempo real\s*\(rtk\)'), ('static',r'precision en post[ -]?proceso\s*\(estatico\)')):
        section = re.search(heading+r'\s*:(.*?)(?=precision en|compensacion de|memoria de|$)', plain)
        if section:
            for axis, label in (('h','horizontal'),('v','vertical')):
                match = re.search(label+r'\s*:\s*[≤<=>]*\s*'+n+r'\s*mm\s*\+\s*'+n+r'\s*ppm', section[1])
                if match:
                    gnss[f'{mode}_{"horizontal" if axis=="h" else "vertical"}_max_mm'] = float(match[1].replace(',','.'))
                    gnss[f'{mode}_ppm_{axis}_max'] = float(match[2].replace(',','.'))
    if re.search(r'sensor imu integrado|imu integrada?', plain):gnss['necesita_imu'] = True
    number(r'(?:angulo minimo de|al menos)\s*'+n+r'\s*(?:grados|°).*?inclinacion', 'inclinacion_imu_min_deg')
    number(r'memoria de almacenamiento\s*:.{0,50}?(?:minimo de|al menos)\s*'+n+r'\s*gb', 'memoria_min_gb')
    if 'memoria interna' in plain and 'memoria_min_gb' in gnss:gnss['memoria_solo_fabrica'] = True
    if re.search(r'formato nativo del fabricante', plain):gnss['registro_propietario'] = True
    number(r'peso.{0,130}?(?:no debera ser mayor a|maximo de|≤)\s*'+n+r'\s*kilogramos', 'peso_max_g', 1000)
    radio = re.search(r'(?:rango de|frecuencia de).{0,20}?'+n+r'\s*mhz\s*a\s*'+n+r'\s*mhz', plain)
    if radio:
        gnss.update(radio_min_mhz=float(radio[1]),radio_max_mhz=float(radio[2]))
    if re.search(r'radio uhf interna.{0,120}?(?:tx/rx|transmisor/receptor)', plain):gnss['uhf_tx_rx_integrada'] = True
    for field in ('bluetooth','wifi'):
        if re.search(r'interfaces inalambricas\s*:.{0,150}?'+('wi[ -]?fi' if field=='wifi' else field), plain):gnss[field] = True
    ip = re.search(r'proteccion contra intemperie\s*:(.*?)(?:resistencia a|rango termico|$)', plain)
    if ip:
        choices = list(dict.fromkeys(re.findall(r'ip\s*(6[78])',ip[1])))
        if choices:gnss['proteccion_ip_aceptada'] = ','.join('IP'+v for v in choices)
    thermal = re.search(r'(?:rango termico de trabajo|temperatura de operacion)\s*:.{0,80}?(-\s*\d+)\s*°?\s*c.{0,25}?\+?'+n+r'\s*°?\s*c', plain)
    if thermal:
        gnss['temperatura_operacion_min_c'] = float(thermal[1].replace(' ',''))
        # «+60 / +65» es ambiguo: se conserva el primer umbral escrito y se avisa.
        gnss['temperatura_operacion_max_c'] = float(thermal[2])
    components = {'gnss':gnss}
    omitted = []
    completar_explicitos(text,components,omitted)
    if re.search(r'usb.{0,20}c\b.{0,40}(?:nativo|directo en (?:el )?receptor)',plain):gnss['usb_c_nativo'] = True
    if re.search(r'rinex.{0,90}(?:directo en (?:el )?receptor|sin conversion)',plain):
        for v in ('2','3'):
            if gnss.get('registro_rinex_'+v):gnss['rinex_'+v+'_nativo'] = True
    if 'inmune a interferencias magneticas' in plain:
        omitted.append('Verificar la inmunidad a interferencias magnéticas de la IMU; disponer de IMU no acredita por sí solo esta condición.')
    quantities=re.search(r'0?(\d+)\s*base\s*y\s*0?(\d+)\s*rovers?',plain)
    if quantities:
        omitted.append(f'Validar oferta de {int(quantities[1])} base y {int(quantities[2])} rovers: configuración de radio, baterías, accesorios y licencias; el ranking evalúa capacidades del modelo, no las unidades incluidas.')
    if thermal and re.search(r'\+?60\s*°?\s*c\s*/\s*\+?65',plain):
        omitted.append('Rango térmico ambiguo +60 °C / +65 °C: se evalúa +60 °C; confirmar si la entidad exige +65 °C. No se sustituye por valores del catálogo.')
    stable = len(gnss)>=15 and 'canales_min' in gnss and 'rtk_horizontal_max_mm' in gnss and 'memoria_min_gb' in gnss
    if not stable:return None
    software = bool(re.search(r'software de oficina|software de procesamiento',plain))
    if software:
        components['software'] = {'rinex':True} if 'rinex' in plain else {}
        for v in ('2','3'):
            if gnss.get('registro_rinex_'+v):components['software']['rinex_'+v] = True
    same_brand = bool(re.search(r'(?:deben|deberan).*?misma marca',plain))
    return {'componentes':components,'omitidos':omitted,'misma_marca':same_brand,'tipo_equipo':'kit' if software or components.get('controladora') else 'gnss'}
