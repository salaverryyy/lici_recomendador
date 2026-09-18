"""Construye una migración revisable; no conecta ni modifica la BD."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app.controladoras import FIELDS

shared=dict(cpu_nucleos=8,ram_gb=4,almacenamiento_gb=64,bateria_mah=9000,
            camara_mp=13,pantalla_tactil=True,teclado_qwerty=True,carga_rapida=True,
            lte_4g=True,bluetooth=True,bluetooth_version='5.0',wifi=True,nfc=True,usb_c=True,usb_otg=True,
            temperatura_operacion_min_c=-20,temperatura_almacenamiento_min_c=-40,
            temperatura_almacenamiento_max_c=70)
models=[('SINGULARXYZ-SC260','SingularXYZ','SC260',{**shared,
    'sistema_operativo':'Android','android_version':11,'procesador':'8 núcleos 2.0 GHz','cpu_ghz':2,
    'expansion_gb':512,'pantalla_pulgadas':5.45,'resolucion_ancho_px':720,'resolucion_alto_px':1440,
    'botones_programables':1,'autonomia_h':18,'carga_h':4,'proteccion_ip':'IP68',
    'temperatura_operacion_max_c':55,'largo_mm':221,'ancho_mm':78,'alto_mm':16.5,
    'wifi_estandar':'IEEE 802.11 a/b/g/n/ac, 2.4/5 GHz',
    'bandas_celulares':'FDD-LTE B1/B2/B3/B4/B5/B7/B8/B12/B17/B20/B28; TDD B34/B38/B39/B40/B41; WCDMA B1/B2/B5/B8; GSM B2/B3/B5/B8',
    'sim':'1 nano SIM; 1 ranura SIM compartida con TF',
    'sensores':'GPS/BDS/GLONASS; G-Sensor, luz, acelerómetro, NFC, flash LED, micrófono, altavoz',
    'software':'Compatibilidad con software de campo de terceros, sin lista específica declarada',
    'notas':'Autonomía: más de 18 h con pantalla encendida. Táctil capacitiva de 5 puntos. Peso, brillo y caída no declarados. No se infiere Wi-Fi 6 ni certificación GMS.',
    'fuente':'SC260 Data Collector, versión 26-08-2025, página 2'}),
    ('SINOGNSS-R60','SinoGNSS','R60',{**shared,
    'sistema_operativo':'Android','android_version':12,'procesador':'Qualcomm 8 núcleos',
    'expansion_gb':128,'pantalla_pulgadas':5.5,'resolucion_ancho_px':1080,'resolucion_alto_px':1920,
    'brillo_nits':500,'botones_programables':4,'teclado_retroiluminado':True,'autonomia_h':30,
    'autofocus':True,'wifi_6':True,'gms':True,'proteccion_ip':'IP67','caida_m':1.6,
    'temperatura_operacion_max_c':65,'peso_g':412,'largo_mm':219.6,'ancho_mm':91.2,'alto_mm':21.2,
    'wifi_estandar':'Wi-Fi 6, 2.4/5 GHz',
    'bandas_celulares':'GSM 850/900/1800/1900; WCDMA B1/B2/B4/B5/B8; LTE-TDD B38/B39/B40/B41; LTE-FDD B1/B2/B3/B4/B5/B7/B8/B12',
    'sensores':'Acelerómetro, giroscopio, luz, NFC, brújula; GPS/A-GPS, GLONASS, BDS, Galileo',
    'software':'Survey Master; ubicación simulada para GIS de terceros; FieldGenius opcional',
    'notas':'Autonomía 30+ h, condiciones no especificadas. Caída sobre concreto. USB 3.0, UART TTL, auriculares digitales. Carga contradictoria: 5 h en página 1 y no más de 4 h en página 2; tiempo de carga sin valor. Frecuencia CPU no declarada.',
    'fuente':'SinoGNSS R60 Data Collector, Ver.2022.08.02, páginas 1-2'})]

def literal(v):
    if v is None:return 'NULL'
    if isinstance(v,bool):return 'TRUE' if v else 'FALSE'
    if isinstance(v,(int,float)):return str(v)
    return "'"+str(v).replace("'","''")+"'"

columns=[]
for key,_,kind,_,_ in FIELDS:
    typ={'text':'TEXT','boolean':'BOOLEAN','number':'NUMERIC'}[kind]
    check=f' CHECK ({key} >= 0)' if kind=='number' and not key.startswith('temperatura_') else ''
    columns.append(f'    {key} {typ}{check}')
lines=['-- Datos verificados contra las fichas aportadas. Sin inferir valores ausentes.',
       'BEGIN;', 'CREATE TABLE IF NOT EXISTS controladora_especificaciones (',
       '    id_equipo TEXT PRIMARY KEY REFERENCES equipos(id_equipo) ON DELETE CASCADE,',
       ',\n'.join(columns),');']
for ident,brand,model,data in models:
    lines.append(f"INSERT INTO equipos(id_equipo,marca,modelo,categoria,descripcion) VALUES ({literal(ident)},{literal(brand)},{literal(model)},'Controladora','Controladora de campo Android con teclado QWERTY') ON CONFLICT(id_equipo) DO NOTHING;")
    values={'id_equipo':ident,**data}
    lines.append('INSERT INTO controladora_especificaciones ('+','.join(values)+') VALUES ('+','.join(literal(v) for v in values.values())+') ON CONFLICT(id_equipo) DO NOTHING;')
lines.append('COMMIT;')
Path('sql/14_controladoras.sql').write_text('\n'.join(lines)+'\n',encoding='utf-8')
