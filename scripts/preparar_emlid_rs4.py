"""Genera una alta idempotente del RS4 estándar con evidencia por campo."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.db import connect

IDENT='GNSS-EMLID-RS4'
VERSION='rs4-auditoria-2026-10-22'
PDF='/media/emlid-rs4/ficha-tecnica-2026.pdf'
WEB='https://emlid.com/reachrs4/'
LOG='https://docs.emlid.com/reachrs4/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/'
IMU='https://blog.emlid.com/imu-tilt-compensation-in-surveying/'
RADIO='https://docs.emlid.com/reachrs4/specifications/specs/'
PRODUCT={
 'id_equipo':IDENT,'marca':'Emlid','modelo':'Reach RS4','categoria':'GNSS',
 'pais_marca':'Hungría','pais_fabricacion':'Pendiente de confirmar',
 'anio_modelo':2025,'publicado':True,'web_url':WEB,'ficha_pdf_url':PDF,
 'imagen_url':'/media/emlid-rs4/portada-horizontal.png',
 'descripcion':'Receptor GNSS RTK base y rover de 672 canales con IMU, 16 GB internos, LTE nano-SIM y radio integrada LoRa/UHF Tx/Rx de hasta 2 W. Sin cámaras; modelo estándar, distinto del RS4 Pro.'}
BASE={
 'id_equipo':IDENT,'tiene_imu':True,'imu_sin_limite_angular':True,
 'imu_generacion':'Segunda generación del algoritmo de compensación (no generación universal del sensor)',
 'imu_tecnologia':'IMU calibrada de fábrica, sin magnetómetro. Inicialización de IMU de 7-10 s con FIX; precisión de inclinación RTK + 2 mm + 0.3 mm/grado. No confundir con tiempo de fijación GNSS.',
 'tiene_camara':False,'cantidad_camaras':0,'mp_camara':0,'laser':False,
 'canales_gnss':672,'memoria':16,'memoria_es_interna':True,
 'autonomia_bateria':16,'bateria_interna':True,'tipo_bateria':'Li-ion interna 5000 mAh, 7.2 V, 36 Wh; carga USB-C PD.',
 'cantidad_baterias':1,'peso_max':927,'tiempo_inicializacion':5,
 'rtk_horizontal_mm':7,'rtk_vertical_mm':14,'rtk_ppm_h':1,'rtk_ppm_v':1,
 'static_horizontal_mm':4,'static_vertical_mm':8,'static_ppm_h':0.5,'static_ppm_v':1,
 'largo_mm':128.6,'ancho_mm':128.6,'alto_mm':99.3,
 'gps':True,'glonass':True,'galileo':True,'beidou':True,'qzss':True,'navic_irnss':True,'constelaciones':6,
 'actualizacion_hz':10,'temperatura_operacion_min_c':-40,'temperatura_operacion_max_c':65,'proteccion_ip':'IP68',
 'usb':True,'usb_c':True,'carga_usb_c':True,'rs232':True,
 'bluetooth':True,'bluetooth_version':'5.1 BR/EDR + LE','wifi':True,'wifi_estandar':'802.11 a/b/g/n',
 'lte_4g':True,'sim_4g':True,'sim_fisica':True,
 'conectividad_nota':'Módem LTE integrado con nano-SIM física; fallback 3G/2G. USB-C para carga PD y datos; Wi-Fi y Bluetooth 5.1. Verificar bandas y servicio celular de la oferta.',
 'uhf_tx_rx_integrada':True,'uhf_modo':'LoRa y UHF integradas Tx/Rx; base y rover',
 'radio_frecuencia':'UHF 410-470 MHz; LoRa 863-870 / 902-928 MHz según región y antena',
 'radio_potencia_max_w':2,'radio_potencia_ajustable':True,'protocolo_multimarca':True,
 'radio_protocolos':'UHF: TRIMTALK 450S, GMSK; LoRa: protocolo propietario Emlid. Potencias/frecuencias dependen de región, antena y configuración; no atribuir otros protocolos UHF.',
 'registro_rinex':True,'registro_rinex_3':True,'rinex_3_directo':True,'registro_propietario':True,
 'formato_propietario':'UBX (binario u-blox; no formato propietario Emlid)',
 'rinex_versiones':'Registro directo RINEX 3.03 documentado; conversión Emlid Studio 1.10 a 3.04. No se presume RINEX 2.x ni todas las revisiones 3.x.',
 'rinex_3_conversion':True,'rinex_conversion_software':'Emlid Studio',
 'rinex_conversion_nota':'Manual RS4/RS4 Pro: RINEX directo y respaldo UBX. Studio 1.10 añade L5 y conversión 3.04; comprobar firmware, archivos y versión. No confundir conversión con registro directo de toda versión.',
 'ambiental_fuente':'RS4 datasheet (LoRa & UHF) 2026.pdf, p.2, Mechanical; manual oficial Reach RS4/RS4 Pro.',
 'ambiental_notas':'Operación -40 a +65 °C, IP68. No se declaran en esta ficha límites de almacenamiento, ensayo de caída, humedad o MIL-STD; quedan pendientes.',
 'tecnica_fuente':'RS4 datasheet (LoRa & UHF) 2026.pdf pp.2-3; manual oficial docs.emlid.com/reachrs4; auditoría 2026-10-22.',
 'tecnica_notas':'RTK 7/14 mm +1 ppm. Estático 4 mm+0.5 ppm H y 8 mm+1 ppm V. PPK 5 mm+0.5 ppm H y 10 mm+1 ppm V, sin confundirlo con estático. Fijación GNSS ~5 s típica; IMU 7-10 s. Salida GNSS hasta 10 Hz, no 20 Hz por inferencia. RS4 estándar sin cámaras ni láser; no es RS4 Pro.',
 'baterias_conectores_fuente':'Ficha RS4 2026 p.2; manual oficial Specifications, puertos USB-C y RS-232.',
 'baterias_conectores_notas':'16 h como rover RTK con inclinación y 22 h de registro; se puntúan 16 h RTK. USB-C PD: 5/9/12/15 V a 3 A. No asumir baterías de repuesto, reemplazo en caliente o elementos incluidos en el kit.',
 'auditoria_fuente':PDF+'; '+WEB,
 'auditoria_notas':'Alta del RS4 estándar; radio LoRa/UHF regional, app de campo Emlid Flow y oficina Emlid Studio. Modelo presentado en octubre de 2025; ficha aportada 2026. País de fabricación pendiente de etiqueta/certificado. Campos no publicados permanecen pendientes.'}

def lit(v):
 if v is None:return 'NULL'
 if isinstance(v,bool):return 'TRUE' if v else 'FALSE'
 if isinstance(v,(int,float)):return str(v)
 return "'"+str(v).replace("'","''")+"'"

def insert(table,row):
 return f'INSERT INTO {table}('+','.join(row)+') VALUES ('+','.join(lit(v) for v in row.values())+') ON CONFLICT(id_equipo) DO NOTHING;'

def main():
 with connect() as conn,conn.cursor() as cur:
  cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='base_evaluacion'")
  columns={r['column_name'] for r in cur.fetchall()}|{'imu_sin_limite_angular'}
 sql=['BEGIN;','ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS imu_sin_limite_angular BOOLEAN;',insert('equipos',PRODUCT),insert('base_evaluacion',BASE)]
 evidence=[]
 for field in sorted(columns-{'id_equipo'}):
  value=BASE.get(field)
  url=PDF
  if field.startswith('rinex') or field in ('registro_rinex','registro_rinex_3','registro_propietario','formato_propietario'):url=LOG
  if field.startswith('imu_'):url=IMU
  if field=='uhf_tx_rx_integrada':url=RADIO
  status='confirmado' if value is not None else 'no_verificado'
  declared=str(value) if value is not None else 'Pendiente de confirmar'
  note='Ficha RS4 estándar pp.2-3 y documentación específica del fabricante; no mezclar RS4 Pro.' if value is not None else 'No confirmado por separado en las fuentes revisadas. No equivale a No y no se deduce de otros modelos.'
  if value is None and (field.startswith('temperatura_camara') or field=='laser_alcance_m' or field.startswith('temperatura_laser')):declared='No aplica';note='RS4 estándar sin cámara ni láser.'
  if field in ('cantidad_baterias_kit','baterias_incluidas_por_receptor'):declared='Depende del kit ofertado';note='No confundir batería interna del receptor con cantidad incluida en la oferta.'
  if field=='inclinacion_imu_deg':
   declared='Sin límite angular impuesto';status='confirmado';url=IMU
   note='No se publica un máximo numérico. Ver declaración IMU sin límite angular; no convertirla en un ángulo inventado.'
  evidence.append(dict(campo=field,valor=value,fuente=url,estado=status,nota=note))
  vals=(IDENT,field,declared,url,'RS4 datasheet (LoRa & UHF) 2026; manual específico RS4',VERSION,status,note)
  sql.append('INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) VALUES ('+','.join(map(lit,vals))+') ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;')
 for low,high in ((410,470),(863,870),(902,928)):
  sql.append(f'INSERT INTO equipo_radio_frecuencia(id_equipo,frecuencia_min_mhz,frecuencia_max_mhz) VALUES ({lit(IDENT)},{low},{high}) ON CONFLICT DO NOTHING;')
 for kind,url,alt,order in [('foto','/media/emlid-rs4/galeria-cuadrada.png','Emlid Reach RS4: imagen cuadrada de estudio',0),('foto','/media/emlid-rs4/portada-horizontal.png','Emlid Reach RS4: portada horizontal expandida',1),('ficha',PDF,'Ficha RS4 LoRa y UHF 2026 aportada por Cotecmi',0)]:
  sql.append('INSERT INTO equipo_archivos(id_equipo,tipo,url,texto_alternativo,orden) SELECT '+','.join(map(lit,(IDENT,kind,url,alt,order)))+f' WHERE NOT EXISTS(SELECT 1 FROM equipo_archivos WHERE id_equipo={lit(IDENT)} AND url={lit(url)});')
 sql.append("INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) SELECT e.id_equipo,'imu_sin_limite_angular','Pendiente de confirmar',COALESCE(e.web_url,''),'Declaración específica de ausencia de límite angular',"+lit(VERSION)+",'no_verificado','No se deduce de una IMU genérica ni de su generación.' FROM equipos e JOIN base_evaluacion b USING(id_equipo) WHERE e.publicado AND e.categoria='GNSS' AND e.id_equipo<>"+lit(IDENT)+" ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;")
 sql.append('COMMIT;')
 (ROOT/'sql/32_emlid_rs4.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
 folder=ROOT/'docs/auditoria/2026-10-22';folder.mkdir(parents=True,exist_ok=True)
 (folder/'emlid-rs4.json').write_text(json.dumps({'equipo':PRODUCT,'evaluacion':BASE,'evidencia':evidence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('RS4:',sum(v is not None for v in BASE.values())-1,'campos técnicos corroborados; evidencia para',len(evidence),'campos.')

if __name__=='__main__':main()
