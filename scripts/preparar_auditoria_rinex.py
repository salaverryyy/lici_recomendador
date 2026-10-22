"""Auditoría reproducible 22-10-2026: solo completa valores corroborados vacíos."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.routers.comparar import COLUMNAS
from app.controladoras import META as CM
from app.slam import META as SM

snapshot=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'tmp/auditoria-20261022/catalogo.json'
rows=json.loads(snapshot.read_text(encoding='utf-8'))
by_id={r['id_equipo']:r for r in rows}
out=ROOT/'docs/auditoria/2026-10-22';out.mkdir(parents=True,exist_ok=True)
changes=[]
VERSION='rinex-auditoria-2026-10-22'

def add(ident,field,value,url,document,note='',table='base_evaluacion'):
    row=by_id[ident]
    data=row['b' if table=='base_evaluacion' else 'c' if table=='controladora_especificaciones' else 's'] or {}
    if data.get(field) is not None:return
    changes.append(dict(id_equipo=ident,tabla=table,campo=field,valor=value,fuente_url=url,documento=document,nota=note))

cru='https://www.comnavtech.com/about/blogs/445.html'
jupiter='https://www.comnavtech.com/uploads/download/Jupiter%20Laser%20RTK%20User%20Guide.pdf'
x1='https://singularxyz.com/download-file/19'
infinity='https://fenix.ciencias.ulisboa.pt/downloadFile/1126037345804184/Leica%20Infinity%20User%20Guide%20v3.1.1.pdf'
trimble='https://help.fieldsystems.trimble.com/tbc/17261.htm'

def conversion(ident,versions,software,url,document,note):
    for v in versions:
        add(ident,'registro_rinex_'+v,True,url,document,note)
        add(ident,'rinex_'+v+'_conversion',True,url,document,note)
    add(ident,'registro_rinex',True,url,document,note)
    add(ident,'rinex_conversion_software',software,url,document,note)
    add(ident,'rinex_conversion_nota',note,url,document,note)

for suffix in ('JUPITER','MARS-PRO','T20','T300PLUS'):
    ident='GNSS-SINOGNSS-'+suffix
    note=('Jupiter WebUI genera directamente RINEX 2.10/3.02. ' if suffix=='JUPITER' else '')+'CRU convierte observaciones ComNav Binary (.cnb) a 2.01/2.11/3.01/3.02/3.03/3.04. El formato bruto del modelo consta en su ficha/manual; comprobar archivo real y versión de CRU. No confundir CRU con Compass Solution ni presuponer licencia incluida.'
    conversion(ident,'23','Compass Receiver Utility (CRU)',cru,'CRU, sección 2.3.4; ficha/manual del receptor que declara ComNav Binary',note)
    add(ident,'rinex_versiones',('Directo WebUI: 2.10, 3.02; ' if suffix=='JUPITER' else '')+'Conversión CRU: 2.01, 2.11, 3.01, 3.02, 3.03, 3.04',cru,'CRU, sección 2.3.4',note)
for v in '23':
    add('GNSS-SINOGNSS-JUPITER','rinex_'+v+'_directo',True,jupiter,'Jupiter User Guide, 3.3.3.2 y 3.3.3.3','WebUI permite CNB, RINEX 2.10 y 3.02; no acredita otras revisiones nativas.')

for ident,r in by_id.items():
    if r['categoria']!='GNSS':continue
    b=r['b'] or {}
    if r['marca']=='Leica':
        note='Leica Infinity Help v3.1.1 (manual del fabricante alojado por universidad), páginas PDF 37 y 45: importa datos MDB de Captivate/SmartWorx y exporta RINEX 2.11/3.02. Confirmar versión de Infinity, funciones/licencia y archivo bruto; la versión nativa del receptor no se ha confirmado.'
        conversion(ident,'23','Leica Infinity',infinity,'Leica Infinity Help v3.1.1, pp. PDF 37 y 45',note)
        add(ident,'rinex_versiones','Conversión Infinity v3.1.1: 2.11, 3.02',infinity,'Leica Infinity Help v3.1.1, exportación GNSS raw data',note)
    if r['marca']=='Trimble':
        note='El registro T02/T04 del modelo se convierte mediante Convert to RINEX; la ayuda oficial admite 2.10, 2.11, 3.02, 3.03, 3.04, 3.05 y 4.01. Requiere Trimble Configuration Utility vigente y archivo bruto compatible. No acredita generación directa en el receptor.'
        conversion(ident,'23','Trimble Convert to RINEX',trimble,'Ayuda oficial TBC, Convert to RINEX; ficha del receptor',note)
        add(ident,'rinex_versiones','Conversión: 2.10, 2.11, 3.02, 3.03, 3.04, 3.05',trimble,'Ayuda oficial Convert to RINEX',note)
        add(ident,'registro_rinex',True,trimble,'Ayuda oficial Convert to RINEX',note)
    if r['marca']=='CHCNAV':
        add(ident,'registro_rinex_2',True,r['web_url'], 'Ficha del fabricante aportada: formatos RINEX 2.11 y 3.02','Se conservan las versiones publicadas; no se acredita toda revisión ni se deduce la modalidad de grabación directa.')
        add(ident,'rinex_conversion_nota','Ficha del fabricante: RINEX 2.11/3.02. La modalidad directa frente a conversión no está verificada por separado.',r['web_url'],'Ficha del fabricante aportada')
    if r['marca']=='Emlid':
        url=('https://docs.emlid.com/reachrs3/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/' if 'RS3' in ident else 'https://docs.emlid.com/reachrs2/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/')
        add(ident,'rinex_3_directo',True,url,'Manual Emlid, Recording RINEX logs on Reach','Emlid Flow configura los registros y descarga RINEX 3.03 del receptor. Verificar firmware y revisión requerida.')
        add(ident,'rinex_3_conversion',True,'https://docs.emlid.com/emlid-studio/reference/changelogs/','Emlid Studio 1.10, 19-08-2026','El conversor incorpora 3.04 desde 1.10; no se traslada esa versión a registro nativo del receptor.')
        add(ident,'rinex_conversion_software','Emlid Studio','https://docs.emlid.com/emlid-studio/convert-to-rinex-workflow/','Convert to RINEX, formatos UBX/RTCM/RINEX')
        add(ident,'rinex_conversion_nota','Registro directo 3.03 configurado con Emlid Flow. Emlid Studio 1.10 permite conversión a 3.04; no se presume registro nativo 3.04 ni RINEX 2.x sin confirmación.','https://docs.emlid.com/emlid-studio/reference/changelogs/','Emlid Studio y documentación de registro Reach')

add('GNSS-SINGULARXYZ-X1','rinex_3_directo',True,x1,'X1-Series User Manual v1.0, p. PDF 9','La configuración Static Data Collection admite XYZ, RINEX 3.02 y 3.04.')
add('GNSS-SINGULARXYZ-X1','rinex_3_conversion',True,x1,'X1-Series User Manual v1.0, pp. PDF 9 y 13','Conversión del formato XYZ con SingularXYZ Converter.')
add('GNSS-SINGULARXYZ-X1','rinex_conversion_software','SingularXYZ Converter',x1,'X1-Series User Manual v1.0, 3.3')
for suffix in ('X1','X1-LITE','ORION-ONE','Z1'):
    ident='GNSS-SINGULARXYZ-'+suffix
    add(ident,'rinex_conversion_nota','La ficha declara RINEX 3.02/3.04 y formato XYZ. No acredita RINEX 2.x. La modalidad directa se marca solo donde el manual del modelo la confirma.',by_id[ident]['web_url'],'Ficha del fabricante y manual del modelo')

# Campos pendientes adicionales, únicamente cuando existe una declaración inequívoca.
for ident,url,doc in (
 ('GNSS-SINGULARXYZ-ORION-ONE','https://www.singularxyz.com/product_detail/Orion_ONE','Interfaz Type-C para datos y carga'),
 ('GNSS-SINGULARXYZ-Z1','https://www.singularxyz.com/product_detail/Z1','Interfaz Type-C para datos y carga'),
 ('GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS','https://www.singularxyz.com/product_detail/Sfaira_ONE_Plus','Carga con power bank por Type-C'),
 ('GNSS-CHCNAV-I73','https://chcnav.com/','i73_DS_EN_Surveyour2.pdf: carga con cargador de teléfono por USB-C'),
 ('GNSS-EMLID-RS2','https://docs.emlid.com/reachrs2/specifications/specs/','Ficha Reach RS2: Charging USB-C'),
 ('GNSS-EMLID-RS2PLUS','https://docs.emlid.com/reachrs2/specifications/specs/','Ficha Reach RS2+: Charging USB-C'),
 ('GNSS-EMLID-RS3','https://docs.emlid.com/reachrs3/specifications/specs/','Ficha Reach RS3: USB Type-C charging')):
    add(ident,'carga_usb_c',True,url,doc,'Se confirma carga, no solo presencia de conector. No cambia la corrección LEMO solo datos.')
for suffix in ('RS2','RS2PLUS','RS3'):
    url='https://docs.emlid.com/reachrs3/firmware-update/connecting-reach-to-the-internet/connecting-to-the-mobile-hotspot/' if suffix=='RS3' else 'https://docs.emlid.com/reachrs2/firmware-update/connecting-reach-to-the-internet/connecting-to-the-internet/'
    add('GNSS-EMLID-'+suffix,'internet_compartido',True,url,'Emlid, conectar Reach a Wi-Fi/Internet para NTRIP','Requiere fuente de Internet externa con LTE y datos, red 2.4 GHz y configuración compatible; no convierte 3.5G interno de RS2 en LTE.')
for suffix in ('X1','X1-LITE'):
    add('GNSS-SINGULARXYZ-'+suffix,'internet_compartido',True,x1,'X1-Series User Manual, flujo RTK / PDA CORS','Modo PDA CORS con software y controladora conectada a Internet; verificar LTE del dispositivo externo.')
lsurl='https://www.comnavtech.com/uploads/soft/20250811/4e5ae729a4210495ed99192713a313ce.pdf'
for field in ('exporta_laz','exporta_ply','exporta_e57'):
    add('SLAM-SINOGNSS-LS600',field,True,lsurl,'Ficha LS600 de ComNav, p.2, RealEditor: Multi-Format Import & Export','Formatos de postproceso mediante RealEditor; verificar versión y licencia. No prueba que esa licencia venga incluida.',table='slam_especificaciones')

def lit(v):
    if v is None:return 'NULL'
    if isinstance(v,bool):return 'TRUE' if v else 'FALSE'
    if isinstance(v,(int,float)):return str(v)
    return "'"+str(v).replace("'","''")+"'"

sql=['BEGIN;']
for field,kind in {'registro_rinex_2':'BOOLEAN','rinex_2_directo':'BOOLEAN','rinex_3_directo':'BOOLEAN',
                   'rinex_2_conversion':'BOOLEAN','rinex_3_conversion':'BOOLEAN',
                   'rinex_conversion_software':'TEXT','rinex_conversion_nota':'TEXT'}.items():
    sql.append(f'ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS {field} {kind};')
for c in changes:
    sql.append(f"UPDATE {c['tabla']} SET {c['campo']}={lit(c['valor'])} WHERE id_equipo={lit(c['id_equipo'])} AND {c['campo']} IS NULL;")
    prefix='slam_' if c['tabla']=='slam_especificaciones' else 'controladora_' if c['tabla']=='controladora_especificaciones' else ''
    values=(c['id_equipo'],prefix+c['campo'],str(c['valor']),c['fuente_url'],c['documento'],VERSION,'confirmado',c['nota'])
    sql.append('INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) VALUES ('+','.join(map(lit,values))+') ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;')
(out/'cambios.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def reason(field,data):
    if field.startswith('ppp_') and data.get('tiene_ppp') is False:return 'No aplica al equipo sin PPP confirmado.'
    if field in ('laser_alcance_m',) and data.get('laser') is False:return 'No aplica: sin láser declarado.'
    if field.startswith('temperatura_camara') and data.get('tiene_camara') is False:return 'No aplica: sin cámara declarada.'
    if field in ('lemo_pines','lemo_solo_datos') and data.get('lemo') is False:return 'No aplica: sin LEMO declarado.'
    if field in ('inclinacion_imu_deg','imu_generacion','imu_tecnologia') and data.get('tiene_imu') is False:return 'No aplica al equipo sin IMU.'
    if field in ('cantidad_baterias_kit','baterias_incluidas_por_receptor'):return 'Depende del kit/oferta, no se deduce de capacidad del equipo.'
    return 'No confirmado en las fuentes revisadas; no equivale a ausencia ni recibe puntos.'

review=[]
for row in rows:
    key,fields=('b',COLUMNAS) if row['categoria']=='GNSS' else ('c',CM) if row['categoria']=='Controladora' else ('s',SM)
    data=row[key] or {}; filled={c['campo'] for c in changes if c['id_equipo']==row['id_equipo']}
    pending={f:reason(f,data) for f in sorted(set(fields)|set(data)) if f!='id_equipo' and data.get(f) is None and f not in filled}
    note=''
    if row['id_equipo']=='SINOGNSS-R60':note='Ficha 2022: texto comercial dice 5 h y tabla no más de 4 h; carga_h queda pendiente por contradicción.'
    if row['id_equipo']=='GNSS-SINGULARXYZ-ORION-ONE':note='Web actual muestra revisión láser distinta. Se conserva alcance validado por Cotecmi para su versión; no se mezclan modelos/revisiones.'
    if row['id_equipo'] in ('GNSS-SINOGNSS-P6H','GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS'):note='No se acredita registro bruto/exportación RINEX 3.x del equipo por pertenecer a una marca o por publicar precisión estática. Pendiente de prueba/documentación específica.'
    review.append(dict(id_equipo=row['id_equipo'],modelo=row['modelo'],categoria=row['categoria'],fuente_equipo=row['web_url'],
                       campos_vacios_antes=sum(f in data and data[f] is None for f in fields),campos_completados_existentes=len(set(fields)&filled&set(data)),
                       campos_pendientes=pending,nota=note))
    prefix='controladora_' if key=='c' else 'slam_' if key=='s' else ''
    for field, explanation in pending.items():
        if field=='carga_h' and row['id_equipo']=='SINOGNSS-R60':explanation=note
        status='No aplica' if explanation.startswith('No aplica') else 'Depende del kit ofertado' if explanation.startswith('Depende del kit') else 'Pendiente de confirmar'
        values=(row['id_equipo'],prefix+field,status,row['web_url'] or '', 'Revisión de ficha/manual y fuentes del fabricante',VERSION,'no_verificado',explanation)
        sql.append('INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) VALUES ('+','.join(map(lit,values))+') ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;')
sql.append('COMMIT;')
(ROOT/'sql/30_rinex_auditoria.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
(out/'revision_catalogo.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Equipos revisados:',len(review),'valores corroborados propuestos:',len(changes),
      'campos existentes completados:',sum(r['campos_completados_existentes'] for r in review))
