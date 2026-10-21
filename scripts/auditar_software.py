"""Actualiza el catálogo documentado y genera una migración incremental reproducible."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'docs/software/catalogo_2026-10-21.json'
rows = json.loads(path.read_text(encoding='utf-8'))

def source(url, scope):
    return {'url': url, 'alcance': scope, 'fecha_consulta': '2026-10-21'}

for row in rows:
    if row['marca'] == 'SinoGNSS':
        row['funciones'].update(dict.fromkeys(('ajuste_red', 'rinex_2', 'rinex_3', 'windows', 'exporta_dxf', 'exporta_csv'), True))
        row['formatos'] = 'Manual V2.0.1: el selector de importación admite RINEX 2.0/3.0 y datos ComNav. Exporta DXF, TXT, KML, informes HTML y CSV de resultados PPK. La admisión de las familias RINEX 2/3 no garantiza todas sus revisiones. El manual limita los datos brutos dinámicos a formato ComNav.'
        row['compatibilidad'] = 'Software del ecosistema SinoGNSS/ComNav. El manual V2.0.1 documenta Windows, ajuste de redes por mínimos cuadrados, ajuste 3D WGS84, 2D local y alturas. Confirmar la versión instalada, formatos de base/rover y requisitos actuales de Windows; no confundir importación RINEX estática con compatibilidad PPK universal.'
        row['licencia'] = 'El manual V2.0.1 exige llave/dongle y su controlador para PPK. Confirmar precio, activación, modalidad e inclusión con el proveedor para la versión ofertada. No confundir con Compass Receiver Utility (CRU) ni Survey Master.'
        row['fuentes'][0]['alcance'] = 'Página oficial: procesamiento estático/cinemático, constelaciones e informes.'
        row['fuentes'].append(source('https://kpn.com.uy/web/wp-content/uploads/2017/12/Compass-Solution_User-Manual_V2.0_Espa%C3%B1ol.pdf', 'Manual ComNav V2.0.1 alojado por el distribuidor KPN: instalación Windows, importación RINEX 2.0/3.0 (selector de archivos en sección 2.2), ajuste por mínimos cuadrados (3.1.4), dongle y datos dinámicos ComNav (3.2), exportación DXF/CSV (4). Contrastado con el manual inglés local de la misma versión.'))
    elif row['marca'] == 'SingularXYZ':
        row['funciones']['windows'] = True
        row['fuentes'].append(source('https://www.singularxyz.com/uploads/files/202506/7f0e2c99c04a5b2883575f5edef93573.pdf', 'Ficha oficial PProcessing, revisión 03-03-2023, página 2: Windows, RINEX 2.x/3.x, ajuste de redes, DXF/CSV e informes HTML. Requisitos actuales de Windows: verificar versión instalada.'))
    else:
        row['funciones'].update(rinex_2=True, rinex_3=True, exporta_csv=True)
        row['formatos'] = 'RINEX y UBX; conversión RTCM3 según flujo. El historial documenta RINEX 2.11 y 3.03 y navegación 2.x/3.x; Studio 1.10 añade RINEX 3.04 en el convertidor. Esto no garantiza cada revisión en todos los modos de procesamiento. Salida POS y CSV corregido en Stop & Go con Emlid Flow; este CSV exige la estructura original de Flow y no equivale a exportación CAD general. Drones RTK con marcas MRK.'
        row['fuentes'].extend([
            source('https://docs.emlid.com/emlid-studio/reference/changelogs/', 'Historial oficial: RINEX 2.11/3.03 y navegación 2.x/3.x; versión 1.10 (19-08-2026) añade 3.04 al convertidor, sin acreditar todos los modos.'),
            source('https://docs.emlid.com/emlid-studio/stop-n-go-with-ef-workflow/', 'Flujo oficial Stop & Go: observaciones RINEX, conversión UBX/RTCM3 y generación de CSV corregido a partir del CSV de Emlid Flow.')])
    # Ejecutar de nuevo el generador no duplica las referencias.
    row['fuentes'] = list({s['url']: s for s in row['fuentes']}.values())

path.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def literal(value):
    return "'" + (json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value).replace("'", "''") + "'"

sql = ['BEGIN;']
for row in rows:
    confirmed = {key: value for key, value in row['funciones'].items() if value is not None}
    assignments = ['funciones = funciones || '+literal(confirmed)+'::jsonb']
    assignments += [key+' = '+literal(row[key])+('::jsonb' if key=='fuentes' else '') for key in ('formatos','compatibilidad','licencia','fuentes')]
    sql.append('UPDATE software_procesamiento SET '+', '.join(assignments)+' WHERE id_software = '+literal(row['id_software'])+';')
sql.append('COMMIT;')
(root/'sql/27_software_auditoria.sql').write_text('\n'.join(sql)+'\n', encoding='utf-8')
