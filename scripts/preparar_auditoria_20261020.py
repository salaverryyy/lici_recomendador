"""Genera SQL e informe reproducibles desde las fuentes revisadas, sin acceder a secretos."""
import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.recomendador import PESOS_AUDITADOS, PESOS_ANTERIORES
VERSION = 'auditoria-2026-10-20'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--snapshot', type=Path, default=ROOT/'tmp/catalog-audit/before.json', help='Inventario previo exportado de equipos, gnss, controladoras y slam (JSON).')
snapshot = json.loads(parser.parse_args().snapshot.read_text(encoding='utf-8'))
docs = {
 'GNSS-CHCNAV-I50': ('ficha_tecnica_GPS-CHC-GNSS-i50.pdf','https://chcnav.com/uploads/i50_DS_EN.pdf'),
 'GNSS-CHCNAV-I73': ('i73_DS_EN_Surveyour2.pdf','https://geospatial.chcnav.com/'),
 'GNSS-CHCNAV-I73PLUS': ('i73+_DS_EN.pdf','https://chcnav.com/dam/jcr%3A00ee4b28-4f64-49a8-8eaa-14cdc03ff129/i73%2B_DS_EN.pdf'),
 'GNSS-CHCNAV-I93': ('i93_DS_EN.pdf','https://geospatial.chcnav.com/'),
 'GNSS-EMLID-RS2': ('Datasheet RS2 ENG web.pdf','https://docs.emlid.com/reachrs2/specifications/specs/'),
 'GNSS-EMLID-RS2PLUS': ('Datasheet-RS2+-ENG-web.pdf','https://emlid.com/reachrs2plus/'),
 'GNSS-EMLID-RS3': ('RS3-Datasheet-UHF.pdf','https://docs.emlid.com/reachrs3/specifications/specs/'),
 'GNSS-LEICA-GS10': ('Leica_Viva_GS10_DS.pdf','https://leica-geosystems.com/-/media/files/leicageosystems/products/brochures/leica_viva_gs10_25_bro.ashx?la=en'),
 'GNSS-LEICA-GS25': ('Leica-Viva-GS25-DS.pdf','https://leica-geosystems.com/-/media/files/leicageosystems/products/brochures/leica_viva_gs10_25_bro.ashx?la=en'),
 'GNSS-LEICA-GS16': ('Leica_Viva_GS16_GNSS_smart_antenna_DS.pdf','https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-viva-gs16'),
 'GNSS-LEICA-GS18': ('Leica_GS18I_DS.pdf','https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-gs18-i'),
 'GNSS-LEICA-GS18T': ('Leica GS18 T BRO.pdf','https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-gs18-t'),
 'GNSS-SINGULARXYZ-X1': ('X1 GNSS Receiver.pdf','https://www.singularxyz.com/product_detail/X1'),
 'GNSS-SINGULARXYZ-X1-LITE': ('X1 Lite GNSS Receiver.pdf','https://www.singularxyz.com/product_detail/X1_Lite'),
 'GNSS-SINGULARXYZ-Z1': ('Z1 GNSS Receiver.pdf','https://www.singularxyz.com/product_detail/Z1'),
 'GNSS-SINGULARXYZ-ORION-ONE': ('_Orion ONE GNSS Receiver (3).pdf','https://www.singularxyz.com/product_detail/Orion_ONE'),
 'GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS': ('_Sfaira ONE Plus GNSS Receiver (1).pdf','https://www.singularxyz.com/product_detail/Sfaira_ONE_Plus'),
 'GNSS-SINOGNSS-JUPITER': ('SinoGNSS Jupiter Laser RTK_ESP.pdf','https://www.comnavtech.com/product/receiver/Jupiter.html'),
 'GNSS-SINOGNSS-MARS-PRO': ('SinoGNSS Mars Pro Laser RTK.pdf','https://www.comnavtech.com/product/receiver/marpro.html'),
 'GNSS-SINOGNSS-T300PLUS': ('SinoGNSS T300 Plus GNSS Receiver.pdf','https://www.comnavtech.com/product/receiver/t300plus.html'),
 'GNSS-SINOGNSS-T20': ('SinoGNSS Receptor GNSS de Mano T20_ES.pdf','https://comnavtech.com/product/receiver/t20.html'),
 'GNSS-SINOGNSS-P6H': ('SinoGNSS P6H Portátil_ES.pdf','https://www.comnavtech.com/'),
 'GNSS-SOUTH-G1': ('ficha_Tecnica_Southern_Galaxy_G1.pdf','https://www.southinstrument.com/company/details/id/77.html'),
 'GNSS-SOUTH-G6': ('ficha_tecnica_South_Galaxy_G6.pdf','https://www.southinstrument.com/company/details/id/77.html'),
 'GNSS-TRIMBLE-R12I': ('022516-511H_Trimble R12i GNSS Receiver.pdf','https://help.fieldsystems.trimble.com/trimble-access/latest/en/equipment-supported.htm'),
 'GNSS-TRIMBLE-R8S': ('Datasheet-Trimble-R8s-GNSS-System-English-USL-Screen.pdf','https://help.fieldsystems.trimble.com/trimble-access/latest/en/equipment-supported.htm'),
 'SINGULARXYZ-SC260': ('_SC260 Data Collector (2).pdf','https://www.singularxyz.com/product_detail/SC260'),
 'SINOGNSS-R60': ('SinoGNSS R60 Data Collector (1).pdf','https://www.comnavtech.com/fr/product/handhold/R60.html'),
 'SINOGNSS-R80': ('SinoGNSS R80 Data Collector_EN.pdf','https://www.comnavtech.com/fr/product/handhold/R80.html'),
 'SLAM-SINGULARXYZ-H1': ('_H1 Handheld 3D Laser Scanner (3).pdf','https://www.singularxyz.com/product_detail/H1_Scanner'),
 'SLAM-SINGULARXYZ-H2': ('_H2 Handheld 3D Laser Scanner (1).pdf','https://singularxyz.com/product_detail/H2_Scanner'),
 'SLAM-SINOGNSS-LS600': ('SinoGNSS LS600 Laser Scanner_EN.pdf','https://www.comnavtech.com/product/3d/LS600.html'),
 'SLAM-GEXCEL-HERON-LITE': ('HERON-LITE_TechSheet.pdf','https://heron.gexcel.it/en/gexcel-solutions-for-3d-surveying/heron-portable-3d-mapping-systems/heron-lite/'),
}

# Solo valores sustentados; ningún NULL se convierte automáticamente en cero/No.
updates = {
 'GNSS-SINOGNSS-MARS-PRO': dict(usb_c=False,rs232=True,lemo=True,lemo_pines=7,registro_propietario=True,formato_propietario='ComNav Binary',imu_generacion='3ª generación',bateria_interna=True,baterias_conectores_notas='Puerto serial LEMO 7 pines; no es USB-C. Dos baterías operativas de 3400 mAh. El protocolo eléctrico RS-232 y la forma del conector son conceptos distintos.'),
 'GNSS-SINOGNSS-JUPITER': dict(usb=True,usb_c=True,vibracion_norma='MIL-STD-810G Method 514.6',lemo=False,rs232=None,bateria_intercambiable=False,bateria_caliente=False,temperatura_camara_min_c=-20,temperatura_camara_max_c=50,registro_propietario=True,formato_propietario='ComNav Binary',baterias_conectores_notas='Type-C. El puerto serial de la web no demuestra RS-232 físico; no confundir con puerto COM virtual. Batería interna recargable.'),
 'GNSS-SINOGNSS-T300PLUS': dict(usb_c=False,bateria_interna=True,registro_propietario=True,formato_propietario='ComNav Binary',vibracion_norma='MIL-STD-810G Method 514.6',baterias_conectores_notas='LEMO 7 pines combina USB y serial. No tiene conector USB-C en la ficha. 8 GB de fábrica; 16/32 GB son opciones al ordenar, no tarjeta externa.'),
 'GNSS-SINOGNSS-T20': dict(autonomia_bateria=13,registro_propietario=True,formato_propietario='ComNav Binary',actualizacion_hz=10,baterias_conectores_notas='Ficha ES 2025.09.04: 13 h típicas, Type-C. Declara comunicación serial sin especificar interfaz eléctrica RS-232; no se infiere.'),
 'GNSS-SINOGNSS-P6H': dict(lemo=False,rs232=False),
 'GNSS-SINGULARXYZ-X1': dict(rs232=True,bateria_interna=True,bateria_intercambiable=False,bateria_caliente=False,rinex_versiones='3.02; 3.04'),
 'GNSS-SINGULARXYZ-X1-LITE': dict(rs232=True,bateria_interna=True,bateria_intercambiable=False,bateria_caliente=False,rinex_versiones='3.02; 3.04'),
 'GNSS-SINGULARXYZ-Z1': dict(lemo=False,rs232=False,bateria_interna=True,bateria_intercambiable=False,bateria_caliente=False,memoria_expandible=True,rinex_versiones='3.02; 3.04'),
 'GNSS-SINGULARXYZ-ORION-ONE': dict(lemo=False,rs232=False,bateria_interna=True,rinex_versiones='3.02; 3.04'),
 'GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS': dict(tiene_camara=False,cantidad_camaras=0,laser=False,wifi=False,uhf_tx_rx_integrada=False,radio_potencia_ajustable=False,radio_potencia_max_w=0,protocolo_multimarca=False,bateria_interna=True,bateria_intercambiable=False,bateria_caliente=False,lemo=False,rs232=False,tecnica_notas='Receptor compacto para CORS por Bluetooth; Type-C para carga y firmware. No atribuir radio UHF, Wi-Fi ni registro estático al no estar declarados. Memoria y registro bruto requieren confirmación.'),
 'GNSS-CHCNAV-I50': dict(usb_c=False,peso_max=1290,bateria_interna=True,humedad_max_pct=100,humedad_condicion='Con condensación',caida_condiciones='Caída de bastón de 2 m; no equivale a caída libre sin bastón.'),
 'GNSS-CHCNAV-I73': dict(lemo=False,rs232=False,uhf_tx_rx_integrada=False,uhf_modo='Rx 430-470 MHz; no transmisión UHF en la revisión 2020',radio_potencia_max_w=0,radio_potencia_ajustable=False,rinex_versiones='2.11; 3.02'),
 'GNSS-CHCNAV-I73PLUS': dict(lemo=False,rs232=False,rinex_versiones='2.11; 3.02'),
 'GNSS-CHCNAV-I93': dict(bateria_caliente=False,baterias_conectores_notas='Batería integrada no extraíble; LEMO 7 pines y USB-C según ficha marzo 2026.'),
 'GNSS-LEICA-GS16': dict(usb_c=False),
 'GNSS-LEICA-GS18T': dict(usb_c=False),
 'GNSS-LEICA-GS18': dict(usb_c=False,cantidad_camaras=1),
 'GNSS-LEICA-GS10': dict(memoria_expandible=True),
 'GNSS-LEICA-GS25': dict(memoria_expandible=True),
 'GNSS-TRIMBLE-R8S': dict(usb=False,usb_c=False,wifi=False,registro_propietario=True,formato_propietario='Trimble T02',baterias_conectores_notas='Puertos seriales y Bluetooth en esta revisión; no atribuir USB-C ni Wi-Fi de receptores Trimble más recientes.'),
 'GNSS-TRIMBLE-R12I': dict(usb_c=False,registro_propietario=True,formato_propietario='Trimble T02/T04'),
 'GNSS-SOUTH-G1': dict(usb_c=False,bateria_interna=True,actualizacion_hz=50,memoria_expandible=True),
 'GNSS-SOUTH-G6': dict(usb_c=False,bateria_interna=True),
 'SINOGNSS-R80': dict(expansion_gb=512,brujula=True,sim='Una SIM y una TF, hasta 512 GB; dos ranuras no significa doble SIM',notas='Auditoría 2026-10-20: ficha EN enero 2026 conserva MediaTek, pantalla 720x1440 y batería 16 h. La página oficial R80 confirma TF hasta 512 GB y brújula electrónica. Dos ranuras corresponden a SIM + TF. CPU GHz, GMS y tiempo de carga siguen sin publicación verificable.'),
 'SINOGNSS-R60': dict(sim='Ranura SIM; formato de tarjeta no especificado en la ficha'),
 'SINGULARXYZ-SC260': dict(wifi_6=False),
 'SLAM-SINGULARXYZ-H1': dict(exporta_laz=None,exporta_dxf=None),
 'SLAM-SINGULARXYZ-H2': dict(),
 'SLAM-SINOGNSS-LS600': dict(exporta_laz=None,exporta_e57=None,exporta_ply=None,formatos_salida='LAS; JPG. Otros formatos requieren confirmar la versión de RealEditor; no inferirlos del software de otros modelos.'),
 'SLAM-GEXCEL-HERON-LITE': dict(cantidad_camaras=0,colorizacion_rgb=False,wifi=True,usb_c=False,notas='HERON LITE sin cámara, no HERON LITE Color. Variante 300 m: cabeza 875 g + bastón 280 g = 1155 g en mano; controladora estándar adicional 1085 g. Pendrive USB 3.1, 256 GB; 512 GB a pedido. No atribuir USB-C del PDA al escáner. IP no publicado para este conjunto.'),
}
for ident in ['GNSS-EMLID-RS2','GNSS-EMLID-RS2PLUS','GNSS-EMLID-RS3']:
    updates[ident] = dict(bateria_interna=True,bateria_caliente=False,registro_rinex_3=True,rinex_versiones='3.03 (Emlid Flow actual)',lemo=False,baterias_conectores_notas='USB-C y conector inferior externo de 9 pines; no se denomina LEMO en el fabricante. RINEX 3.03 confirmado por la guía Emlid Flow de registro PPK.')
    updates[ident]['uhf_tx_rx_integrada'] = False
    updates[ident]['uhf_modo'] = 'LoRa Tx/Rx 868/915 MHz; '+('UHF 410–470 MHz solo recepción (TRIMTALK 450S), no transmisión en esa banda.' if ident=='GNSS-EMLID-RS3' else 'sin radio integrada Tx/Rx en banda 410–470 MHz.')

for row in snapshot['gnss']:
    ident = row['id_equipo']
    row['memoria_es_interna'] = None
    if ident != 'GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS':
        updates.setdefault(ident,{})['memoria_es_interna'] = ident not in (
            'GNSS-LEICA-GS10','GNSS-LEICA-GS25','GNSS-LEICA-GS16',
        )

# Conserva deliberadamente la ficha/version aportada cuando la web corresponde a otra revisión.
notes = {
 'GNSS-SINOGNSS-MARS-PRO':'La ficha aportada declara 32 GB y la web actual 8 GB; se conserva 32 GB de la ficha con advertencia de variante. USB genérico no confirmado; LEMO/serial no implica USB-C.',
 'GNSS-SINOGNSS-T20':'Se corrige 20 h a 13 h de la ficha ES aportada, no las 20 h de otra revisión web.',
 'GNSS-CHCNAV-I50':'Peso y Mini-USB del datasheet oficial i50; confirmar revisión frente a ficha comercial aportada.',
 'SLAM-SINOGNSS-LS600':'Se conserva configuración 32 líneas/300 m del catálogo: existen 16 líneas/120 m. Precisión 1 cm es relativa posprocesada; absoluta 3 cm. No equiparar ambas.',
 'SLAM-SINGULARXYZ-H1':'LAZ y DXF no figuran en la lista de salida de esta ficha; no confundir con H2. Software compatible no prueba licencia incluida.',
 'SLAM-SINGULARXYZ-H2':'GNSS es opcional. 70 m requiere reflectividad >80%; 40 m a >10%. 1 cm está especificado a 10 m.',
 'SLAM-GEXCEL-HERON-LITE':'Se conserva la revisión de la ficha aportada: no mezclar temperatura, peso o cámara con fichas antiguas/Color.',
}

def literal(value):
    if value is None: return 'NULL'
    if value is True: return 'TRUE'
    if value is False: return 'FALSE'
    if isinstance(value,(int,float)): return str(value)
    return "'" + str(value).replace("'", "''") + "'"

sql = ['BEGIN;', '-- Datos trazables: no se inventan especificaciones para eliminar NULL.',
       'ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS memoria_es_interna BOOLEAN;']
report = []
for equipment in snapshot['equipos']:
    ident = equipment['id_equipo']
    group,table,prefix = ('controladoras','controladora_especificaciones','controladora_') if equipment['categoria']=='Controladora' else ('slam','slam_especificaciones','slam_') if equipment['categoria']=='Escáner SLAM' else ('gnss','base_evaluacion','')
    current = next(r for r in snapshot[group] if r['id_equipo']==ident)
    changes = updates.get(ident,{})
    document,url = docs[ident]
    if changes:
        assert all(k in current for k in changes), (ident,set(changes)-set(current))
        sql.append('UPDATE '+table+' SET '+', '.join(k+'='+literal(v) for k,v in changes.items())+' WHERE id_equipo='+literal(ident)+';')
    if group=='gnss':
        audit_note='Auditoría 2026-10-20: '+notes.get(ident,'Se revisa la ficha aportada y se clasifican campos no publicados sin inventar valores. Ver evidencia por campo.')
        sql.append('UPDATE base_evaluacion SET auditoria_fuente='+literal(document+'; '+url+'; auditoría 2026-10-20')+', auditoria_notas=CASE WHEN COALESCE(auditoria_notas,\'\') LIKE \'%Auditoría 2026-10-20:%\' THEN auditoria_notas ELSE CONCAT_WS(\' \',auditoria_notas,'+literal(audit_note)+') END WHERE id_equipo='+literal(ident)+';')
    sql.append('UPDATE equipos SET web_url=COALESCE(web_url,'+literal(url)+') WHERE id_equipo='+literal(ident)+';')
    merged = {**current,**changes}
    unresolved = []
    not_applicable = []
    for field,value in merged.items():
        if field == 'id_equipo': continue
        changed = field in changes
        if value is not None and not changed: continue
        state = 'confirmado' if value is not None else 'no_verificado'
        declared = str(value) if value is not None else 'No publicado por el fabricante'
        note = notes.get(ident,'Ficha técnica y documentación del fabricante revisadas; las opciones comerciales deben confirmarse en la oferta.')
        if value is None:
            if ((field.startswith('temperatura_camara') or field=='mp_camara') and merged.get('tiene_camara') is False) or (field in ('imu_generacion','imu_tecnologia','inclinacion_imu_deg') and merged.get('tiene_imu') is False) or (field in ('ppp_h_cm','ppp_v_cm') and merged.get('tiene_ppp') is False) or (field=='laser_alcance_m' and merged.get('laser') is False) or (field=='lemo_pines' and merged.get('lemo') is False) or (field=='resolucion_camara_mp' and merged.get('cantidad_camaras')==0):
                declared,state = 'No aplica','confirmado'
                not_applicable.append(field)
            else:
                unresolved.append(field)
                if 'kit' in field or field=='baterias_incluidas_por_receptor':
                    declared='Depende del kit ofertado'
                elif field.startswith(('red_rtk','largo_static')):
                    declared='Modo no especificado por separado'
            note = declared+'. '+note
        values=[ident,prefix+field,declared,url,document,VERSION,None,state,note]
        sql.append('INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,pagina,estado,nota) VALUES ('+','.join(literal(v) for v in values)+") ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO UPDATE SET valor_declarado=EXCLUDED.valor_declarado,documento=EXCLUDED.documento,pagina=EXCLUDED.pagina,estado=EXCLUDED.estado,nota=EXCLUDED.nota,fecha_consulta=CURRENT_DATE;")
    report.append(dict(id_equipo=ident,marca=equipment['marca'],modelo=equipment['modelo'],categoria=equipment['categoria'],documento=document,fuente=url,cambios=changes,no_publicados=unresolved,no_aplica=not_applicable,nota=notes.get(ident,'')))
for key,weight in PESOS_AUDITADOS.items():
    sql.append('UPDATE reglas_recomendacion SET peso='+str(weight)+' WHERE criterio='+literal(key)+' AND peso='+str(PESOS_ANTERIORES[key])+' AND activo=TRUE;')
sql.append('COMMIT;')
(ROOT/'sql/25_auditoria_integral.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
out=ROOT/'docs/auditoria/2026-10-20'
out.mkdir(parents=True,exist_ok=True)
(out/'catalogo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Equipos:',len(report),'valores contrastados:',sum(len(r['cambios']) for r in report),'no publicados:',sum(len(r['no_publicados']) for r in report),'no aplica:',sum(len(r['no_aplica']) for r in report))
