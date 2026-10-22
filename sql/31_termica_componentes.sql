BEGIN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS temperatura_laser_min_c NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS temperatura_laser_max_c NUMERIC;

-- El bloque -20/+50 de la ficha Jupiter pertenece al láser, no a la cámara.
-- No borrar una edición posterior que ya no tenga ambos valores erróneos.
UPDATE base_evaluacion SET temperatura_camara_min_c=NULL,temperatura_camara_max_c=NULL
WHERE id_equipo='GNSS-SINOGNSS-JUPITER' AND temperatura_camara_min_c=-20 AND temperatura_camara_max_c=50;
UPDATE base_evaluacion SET temperatura_laser_min_c=-20 WHERE id_equipo='GNSS-SINOGNSS-JUPITER' AND temperatura_laser_min_c IS NULL;
UPDATE base_evaluacion SET temperatura_laser_max_c=50 WHERE id_equipo='GNSS-SINOGNSS-JUPITER' AND temperatura_laser_max_c IS NULL;
UPDATE base_evaluacion SET ambiental_fuente='SinoGNSS Jupiter Laser RTK_ESP.pdf, Ver.2025.08.06, p.1; ficha oficial ComNav 2025.03.26. Auditoría térmica 2026-10-22.',
 ambiental_notas='Receptor GNSS: -40 a +65 °C. Láser: -20 a +50 °C (almacenamiento láser -30 a +60 °C). La ficha no publica un rango térmico separado para cámara. No trasladar límites del láser a cámara ni al receptor.'
WHERE id_equipo='GNSS-SINOGNSS-JUPITER';

INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota)
SELECT 'GNSS-SINOGNSS-JUPITER',field,value,'https://www.comnavtech.com/uploads/soft/20250415/424636fc51274f14ead63b6ac83be845.pdf',
 'SinoGNSS Jupiter Laser RTK; contraste visual con ficha ESP Ver.2025.08.06 p.1', 'termica-componentes-2026-10-22',status,note
FROM (VALUES
 ('temperatura_operacion_min_c','-40','confirmado','Bloque Especificaciones Ambientales del receptor.'),
 ('temperatura_operacion_max_c','65','confirmado','Bloque Especificaciones Ambientales del receptor.'),
 ('temperatura_laser_min_c','-20','confirmado','Bloque Especificaciones Láser; no pertenece a cámara.'),
 ('temperatura_laser_max_c','50','confirmado','Bloque Especificaciones Láser; no pertenece a cámara.'),
 ('temperatura_camara_min_c','No publicado por separado','no_verificado','Se rectifica la atribución anterior: -20 °C corresponde al láser, no a la cámara. Se usa el rango general salvo restricción documentada.'),
 ('temperatura_camara_max_c','No publicado por separado','no_verificado','Se rectifica la atribución anterior: +50 °C corresponde al láser, no a la cámara. Se usa el rango general salvo restricción documentada.')
) AS evidence(field,value,status,note)
ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;

INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota)
SELECT 'GNSS-SINGULARXYZ-ORION-ONE',field,value,'https://www.singularxyz.com/Orion_ONE.html',
 'Orion ONE Series GNSS Receiver; contraste con ficha aportada Version 04-03-2026 p.1', 'termica-componentes-2026-10-22','confirmado',note
FROM (VALUES
 ('temperatura_operacion_min_c','-40','Tabla ENVIRONMENTAL del receptor; no se inventa un rango específico para cámara o láser.'),
 ('temperatura_operacion_max_c','65','Tabla ENVIRONMENTAL del receptor; no se inventa un rango específico para cámara o láser.'),
 ('cantidad_camaras','1','VISUAL SENSOR: una cámara global shutter de 2 MP. No equivale a doble cámara por incluir láser o AR.')
) AS evidence(field,value,note)
ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;

-- Los nuevos campos no se rellenan con el rango del receptor por deducción.
INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota)
SELECT e.id_equipo,field,CASE WHEN b.laser=FALSE THEN 'No aplica' ELSE 'Pendiente de confirmar' END,
 COALESCE(e.web_url,''),'Revisión de rangos térmicos específicos por componente', 'termica-componentes-2026-10-22','no_verificado',
 'Sin un rango específico confirmado del láser no se copia la temperatura general ni la de la cámara.'
FROM equipos e JOIN base_evaluacion b USING(id_equipo)
CROSS JOIN (VALUES ('temperatura_laser_min_c'),('temperatura_laser_max_c')) AS fields(field)
WHERE e.publicado AND e.categoria='GNSS' AND e.id_equipo<>'GNSS-SINOGNSS-JUPITER'
ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;
COMMIT;
