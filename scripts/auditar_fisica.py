"""Genera la migración y el informe de peso/dimensiones con evidencia por modelo.

No consulta la base ni completa pesos por analogía. Las cifras proceden de las
fichas del fabricante aportadas y las fuentes primarias revisadas el 23-10-2026.
"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'fisica-2026-10-23'

# ID, peso (g), dimensiones (mm en el orden publicado), forma.
GNSS = [
 ('CHCNAV-I50',1290,(140,130,106),'caja'),
 ('CHCNAV-I73',730,(119,119,85),'caja'),
 ('CHCNAV-I73PLUS',730,(119,119,85),'caja'),
 ('CHCNAV-I93',1150,(152,152,81),'diametro'),
 ('EMLID-RS2',950,(126,126,142),'caja'),
 ('EMLID-RS2PLUS',950,(126,126,142),'caja'),
 ('EMLID-RS3',950,(126,126,142),'caja'),
 ('EMLID-RS4',927,(128.6,128.6,99.3),'caja'),
 ('LEICA-GS10',1200,(212,166,79),'caja'),
 ('LEICA-GS16',930,(190,190,90),'diametro'),
 ('LEICA-GS18',1250,(173,173,109),'caja'),
 ('LEICA-GS18T',1230,(173,173,109),'caja'),
 ('LEICA-GS25',1840,(220,200,94),'caja'),
 ('SINGULARXYZ-ORION-ONE',547,(107,107,58.7),'diametro'),
 ('SINGULARXYZ-SFAIRA-ONE-PLUS',409,(50,50,149),'diametro'),
 ('SINGULARXYZ-X1',870,(133.5,133.5,67),'diametro'),
 ('SINGULARXYZ-X1-LITE',870,(133.5,133.5,67),'diametro'),
 ('SINGULARXYZ-Z1',547,(107,107,58.7),'diametro'),
 ('SINOGNSS-JUPITER',810,(133.5,133.5,66),'diametro'),
 ('SINOGNSS-MARS-PRO',1200,(155,155,73),'diametro'),
 ('SINOGNSS-P6H',310,(181,83,17.4),'caja'),
 ('SINOGNSS-T20',670,(149,149,48),'diametro'),
 ('SINOGNSS-T300PLUS',950,(158,158,75),'diametro'),
 ('SOUTH-G1',1000,(129,129,112),'diametro'),
 ('SOUTH-G6',1440,(152,152,137),'diametro'),
 ('TRIMBLE-R12I',1120,(119,119,136),'diametro'),
 ('TRIMBLE-R8S',1520,(190,190,104),'diametro'),
]
CONTROLLERS = [
 ('SINOGNSS-R60',412,(219.6,91.2,21.2)),
 ('SINOGNSS-R80',488,(242,87.6,24)),
 ('SINGULARXYZ-SC260',None,(221,78,16.5)),
]

def sources():
    tree = ast.parse((ROOT/'scripts/preparar_auditoria_20261020.py').read_text(encoding='utf-8'))
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='docs' for t in n.targets))

def build_records():
    refs = sources()
    refs['GNSS-EMLID-RS4'] = ('RS4 datasheet (LoRa & UHF) 2026.pdf','https://emlid.com/reachrs4/')
    refs['SLAM-GEXCEL-HERON-LITE'] = ('HERON-LITE_TechSheet.pdf, pp.1-2','https://www.gexcel.it/images/soluzioni/HERON/HERON-LITE_TechSheet.pdf')
    refs['GNSS-SOUTH-G1'] = (refs['GNSS-SOUTH-G1'][0],'https://www.southinstrument.com/product/details/pro_tid/3/id/10.html')
    refs['SINOGNSS-R60'] = (refs['SINOGNSS-R60'][0],'https://www.comnavtech.com/product/handheld/r60.html')
    refs['SINOGNSS-R80'] = (refs['SINOGNSS-R80'][0],'https://www.comnavtech.com/uploads/soft/20250925/81426acc56e9cd2b10445f9b8292e2ec.pdf')
    for ident,url in {
      'GNSS-CHCNAV-I73':'https://chcnav.ee/datasheets/i73_DS_EN.pdf',
      'GNSS-CHCNAV-I93':'https://chcnav.com/uploads/i93_DS_EN.pdf',
      'GNSS-SOUTH-G6':'https://www.southinstrument.com/uploads/file/2020-09-24/5f6c49f64ca1c.pdf',
      'GNSS-SINOGNSS-JUPITER':'https://www.comnavtech.com/uploads/soft/20250707/1974fbf6ae0dde3ac748cedd800b5218.pdf',
      'GNSS-SINOGNSS-T20':'https://www.comnavtech.com/sp/product/receiver/t20.html',
      'GNSS-SINOGNSS-MARS-PRO':'https://www.comnavtech.com/uploads/soft/20240530/0b3121da45cdff99ec0af46af5481c2f.pdf',
      'SLAM-SINOGNSS-LS600':'https://www.comnavtech.com/uploads/soft/20250709/6c096eb196a3d8fdeba51445716ea8c9.pdf',
      'SLAM-SINGULARXYZ-H1':'https://singularxyz.com/download-file/90',
      'SINGULARXYZ-SC260':'https://www.singularxyz.com/uploads/files/202509/eb3ca89d82ac0b6adba04ffe366598c7.pdf',
    }.items():refs[ident]=(refs[ident][0],url)
    notes = {
      'SINOGNSS-MARS-PRO':'1200 g con las dos baterías; sin bastón ni controladora.',
      'SINOGNSS-T300PLUS':'950 g con las dos baterías; sin bastón ni controladora.',
      'SINOGNSS-JUPITER':'810 g con batería interna; sin bastón ni controladora.',
      'TRIMBLE-R12I':'1120 g con batería interna, radio interna y antena UHF. El conjunto con bastón, TSC7 y soporte pesa 3950 g; no se usa ese total como peso del receptor.',
      'TRIMBLE-R8S':'1520 g con batería interna, radio y antena. Dimensiones incluyen conectores; no confundir con los 3810 g del conjunto con bastón/controladora.',
      'SOUTH-G1':'1000 g con batería; corresponde a New Galaxy G1, no G1 Plus ni G1 IMU de otra generación.',
      'SOUTH-G6':'1440 g incluyendo batería; no sustituir por otro Galaxy de nombre parecido.',
      'LEICA-GS16':'930 g declarados para la antena; 3200 g corresponden al rover completo sobre bastón. La ficha no desglosa por separado batería y radio.',
      'LEICA-GS18':'1250 g del GS18 I (con cámara), modelo al que corresponde este registro y su ficha; 3550 g son el conjunto sobre bastón. No trasladar el peso del GS18 sin cámara.',
      'LEICA-GS18T':'1230 g del GS18 T; 3530 g son el rover completo sobre bastón. No mezclar con GS18 I.',
      'LEICA-GS10':'1200 g declarados para el receptor GS10; no incluyen el conjunto de 5400 g con bastón/mochila. La ficha no acredita el peso completo con antena externa y todos los accesorios.',
      'LEICA-GS25':'1840 g declarados para el receptor GS25; no equivalen al conjunto completo con antena externa, baterías y accesorios. La ficha no desglosa el peso operativo total.',
      'SINOGNSS-P6H':'310 g declarados. Se conservan 181 × 83 × 17.4 mm de la ficha ES aportada. Hay conflicto entre revisiones: la web y ficha EN 2024.3.1 publican 165.5 × 81.6 × 29.1 mm. Verificar revisión/medida física de la unidad; no mezclar con P6C. Contraste: https://www.comnavtech.com/product/handheld/P6H.html y https://sinognss.com/uploads/soft/20250401/fbaa3b3bf721afd6a44a5aa036ad072d.pdf',
      'SINOGNSS-T20':'670 g declarados; dimensiones nominales Ø149 × 48 mm, tolerancia publicada ±1 mm.',
    }
    records=[]
    for suffix,weight,dims,shape in GNSS:
        ident='GNSS-'+suffix
        dimension=(f'Ø{dims[0]:g} × {dims[2]:g} mm (diámetro × alto). Los campos largo y ancho representan el mismo diámetro.'
                   if shape=='diametro' else ' × '.join(f'{x:g}' for x in dims)+' mm (orden de la ficha).')
        note=notes.get(suffix,f'{weight} g declarados para el receptor. La ficha no desglosa por separado todos los accesorios o condiciones de pesada; no atribuir el peso a un kit completo.')
        doc,url=refs[ident]
        records.append(dict(id_equipo=ident,tabla='base_evaluacion',peso_campo='peso_max',peso_g=weight,dimensiones_mm=dims,dimensiones_declaradas=dimension,peso_condiciones=note,documento=doc,fuente_url=url))
    for ident,weight,dims in CONTROLLERS:
        doc,url=refs[ident]
        note=f'{weight} g con batería, según ficha del fabricante; sin soporte de bastón.' if weight else 'Peso no publicado en la ficha SC260 de 26-08-2025, página oficial ni manual revisados. Pendiente de pesaje o confirmación escrita del fabricante; no usar el peso de SC300 ni del embalaje de un kit.'
        records.append(dict(id_equipo=ident,tabla='controladora_especificaciones',peso_campo='peso_g',peso_g=weight,dimensiones_mm=dims,dimensiones_declaradas=' × '.join(f'{x:g}' for x in dims)+' mm (largo × ancho × espesor).',peso_condiciones=note,documento=doc,fuente_url=url))
    slams=[
      ('SLAM-SINGULARXYZ-H1',1242,'Cuerpo: 120 × 145 × 85 mm, sin empuñadura. Empuñadura-batería: 64 × 158 × 38 mm. No se publica la envolvente del conjunto montado.', '900 g de cuerpo + una empuñadura-batería de 342 g = 1242 g en uso manual. La segunda empuñadura es repuesto, no se suma al peso en mano.'),
      ('SLAM-SINGULARXYZ-H2',1225,'Cuerpo: 115 × 113 × 120 mm, sin empuñadura. No se publican las dimensiones de la empuñadura ni la envolvente montada.', '740 g de cuerpo + empuñadura-batería de 485 g = 1225 g. No incluye teléfono, soporte ni módulo GNSS opcional.'),
      ('SLAM-SINOGNSS-LS600',1900,'240 × 115 × 320 mm (largo × ancho × alto), configuración de la ficha.', '1900 g con batería de mano y placa para puntos de control (nota 1 de la ficha aportada). Otras revisiones publican 2300 g o un límite menor a 2700 g; no intercambiar revisiones/configuraciones sin verificar la unidad ofertada.'),
      ('SLAM-GEXCEL-HERON-LITE',2240,'Variante 300 m sin cámara: cabeza 207 × 122 mm, Ø104 mm. Bastón telescópico de 400 a 1300 mm; altura montada de 570 a 1470 mm. Caja estándar: 160 × 209 × 59 mm. PDA: 173 × 80 × 11 mm. Son componentes separados, no una caja envolvente única.', 'Cabeza 875 g + bastón 280 g = 1155 g en mano; caja de control estándar con batería 1085 g. Total de esos componentes: 2240 g; PDA adicional 250 g. Caja rugged opcional 2150 g. No confundir con HERON LITE Color ni la cabeza 120 m de 1350 g.'),
    ]
    for ident,weight,dimension,note in slams:
        doc,url=refs[ident]
        records.append(dict(id_equipo=ident,tabla='slam_especificaciones',peso_campo='peso_operativo_g',peso_g=weight,dimensiones_mm=None,dimensiones_declaradas=dimension,peso_condiciones=note,documento=doc,fuente_url=url))
    return records

def lit(value):
    if value is None:return 'NULL'
    if isinstance(value,(int,float)):return str(value)
    return "'"+str(value).replace("'","''")+"'"

def main():
    records=build_records()
    sql=['BEGIN;']
    for table in ('base_evaluacion','controladora_especificaciones','slam_especificaciones'):
        for field in ('dimensiones_declaradas','peso_condiciones','fisica_fuente'):
            sql.append(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {field} TEXT;')
    for row in records:
        vals={row['peso_campo']:row['peso_g'], 'dimensiones_declaradas':row['dimensiones_declaradas'], 'peso_condiciones':row['peso_condiciones'], 'fisica_fuente':row['documento']+'; '+row['fuente_url']+'; consulta 2026-10-23.'}
        if row['dimensiones_mm']:
            vals.update(zip(('largo_mm','ancho_mm','alto_mm'),row['dimensiones_mm']))
        sql.append('UPDATE '+row['tabla']+' SET '+','.join(k+'='+lit(v) for k,v in vals.items())+' WHERE id_equipo='+lit(row['id_equipo'])+';')
        prefix='controladora_' if row['tabla']=='controladora_especificaciones' else 'slam_' if row['tabla']=='slam_especificaciones' else ''
        for field,value in vals.items():
            status='confirmado' if value is not None else 'no_verificado'
            if row['id_equipo']=='GNSS-SINOGNSS-P6H' and field in ('largo_mm','ancho_mm','alto_mm'):status='no_verificado'
            declared=str(value) if value is not None else 'Pendiente de confirmar'
            note=row['peso_condiciones'] if field==row['peso_campo'] or row['id_equipo']=='GNSS-SINOGNSS-P6H' else row['dimensiones_declaradas']
            evidence=(row['id_equipo'],prefix+field,declared,row['fuente_url'],row['documento'],VERSION,status,note)
            sql.append('INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota) VALUES ('+','.join(map(lit,evidence))+') ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;')
    sql.append('COMMIT;')
    (ROOT/'sql/33_peso_dimensiones.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
    folder=ROOT/'docs/auditoria/2026-10-23';folder.mkdir(parents=True,exist_ok=True)
    (folder/'peso-dimensiones.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=['# Auditoría de peso y dimensiones — 2026-10-23','',
      '34 equipos: 27 GNSS, 3 controladoras y 4 SLAM. Software de oficina no tiene peso ni dimensiones físicos.',
      'Se contrastaron las fichas del fabricante aportadas con páginas y documentos oficiales. No se usan medidas de embalaje, de otra generación ni pesos estimados por apariencia.',
      'Las dimensiones SLAM se publican por componente cuando no existe envolvente montada. Las notas no otorgan puntos adicionales.',
      'Único peso pendiente: SC260, no publicado en las fuentes revisadas. P6H conserva la revisión ES, con conflicto de dimensiones explícito. No se afirma cobertura numérica total cuando el fabricante no la permite.',
      '', '| Equipo | Peso declarado/evaluado (g) | Dimensiones y alcance | Fuente |','|---|---:|---|---|']
    for r in records:
        report.append(f"| {r['id_equipo']} | {r['peso_g'] if r['peso_g'] is not None else 'No publicado'} | {r['dimensiones_declaradas']} | [{r['documento']}]({r['fuente_url']}) |")
    report+=['','## Condiciones y conflictos por modelo','']
    for r in records:report.append(f"- **{r['id_equipo']}**: {r['peso_condiciones']}")
    (folder/'peso-dimensiones.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(f'{len(records)} equipos auditados; 33 pesos numéricos y 34 descripciones de dimensiones con alcance.')

if __name__=='__main__':main()
