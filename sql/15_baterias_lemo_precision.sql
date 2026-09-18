BEGIN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS cantidad_baterias INTEGER CHECK(cantidad_baterias>0);
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS cantidad_baterias_kit INTEGER CHECK(cantidad_baterias_kit>0);
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS lemo BOOLEAN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS lemo_pines INTEGER CHECK(lemo_pines>0);
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS baterias_conectores_fuente TEXT;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS baterias_conectores_notas TEXT;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS red_rtk_horizontal_mm NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS red_rtk_vertical_mm NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS red_rtk_ppm_h NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS red_rtk_ppm_v NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS largo_static_horizontal_mm NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS largo_static_vertical_mm NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS largo_static_ppm_h NUMERIC;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS largo_static_ppm_v NUMERIC;

-- Cantidad de bloques de batería del receptor; NO celdas ni repuestos de kits.
UPDATE base_evaluacion SET cantidad_baterias=2 WHERE id_equipo IN ('GNSS-CHCNAV-I50','GNSS-SINOGNSS-MARS-PRO','GNSS-SINOGNSS-T300PLUS');
UPDATE base_evaluacion SET cantidad_baterias=1 WHERE id_equipo IN ('GNSS-EMLID-RS2','GNSS-EMLID-RS2PLUS','GNSS-EMLID-RS3','GNSS-TRIMBLE-R8S','GNSS-TRIMBLE-R12I','GNSS-LEICA-GS16','GNSS-LEICA-GS18T','GNSS-LEICA-GS18','GNSS-CHCNAV-I73','GNSS-CHCNAV-I73PLUS','GNSS-CHCNAV-I93','GNSS-SOUTH-G1','GNSS-SOUTH-G6','GNSS-SINOGNSS-JUPITER','GNSS-SINOGNSS-P6H');
UPDATE base_evaluacion SET cantidad_baterias_kit=4,baterias_conectores_notas='El receptor usa dos baterías intercambiables. El kit mostrado incluye cuatro baterías de litio; no se cuentan cuatro simultáneas.' WHERE id_equipo='GNSS-CHCNAV-I50';
UPDATE base_evaluacion SET baterias_conectores_notas='La ficha describe una batería extraíble del receptor. El paquete opcional de cuatro baterías no es la cantidad simultánea. USB de 7 pines distinto del LEMO de 5 pines.' WHERE id_equipo='GNSS-SOUTH-G1';
UPDATE base_evaluacion SET baterias_conectores_notas='Una batería extraíble descrita. USB de 7 pines distinto del LEMO de 5 pines.' WHERE id_equipo='GNSS-SOUTH-G6';
UPDATE base_evaluacion SET baterias_conectores_notas='Cantidad no declarada explícitamente; no se deduce de la capacidad en mAh.' WHERE id_equipo IN ('GNSS-SINGULARXYZ-X1','GNSS-SINGULARXYZ-X1-LITE','GNSS-SINGULARXYZ-Z1','GNSS-SINGULARXYZ-ORION-ONE','GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS');
UPDATE base_evaluacion SET lemo=TRUE,lemo_pines=7 WHERE id_equipo IN ('GNSS-TRIMBLE-R12I','GNSS-TRIMBLE-R8S','GNSS-CHCNAV-I93','GNSS-SINOGNSS-MARS-PRO','GNSS-SINOGNSS-T300PLUS','GNSS-SINGULARXYZ-X1','GNSS-SINGULARXYZ-X1-LITE');
UPDATE base_evaluacion SET lemo=TRUE,lemo_pines=5 WHERE id_equipo IN ('GNSS-SOUTH-G1','GNSS-SOUTH-G6');
UPDATE base_evaluacion SET lemo=TRUE WHERE id_equipo IN ('GNSS-LEICA-GS16','GNSS-LEICA-GS18T','GNSS-LEICA-GS18');
UPDATE base_evaluacion SET baterias_conectores_fuente=tecnica_fuente WHERE id_equipo LIKE 'GNSS-%';

-- Cada modo conserva sus propios valores; nunca sustituir línea base por red.
UPDATE base_evaluacion SET red_rtk_horizontal_mm=8,red_rtk_vertical_mm=15,red_rtk_ppm_h=0.5,red_rtk_ppm_v=0.5 WHERE id_equipo IN ('GNSS-SINOGNSS-MARS-PRO','GNSS-TRIMBLE-R12I','GNSS-TRIMBLE-R8S','GNSS-LEICA-GS16','GNSS-LEICA-GS18T','GNSS-LEICA-GS18');
UPDATE base_evaluacion SET largo_static_horizontal_mm=3,largo_static_vertical_mm=3.5,largo_static_ppm_h=0.1,largo_static_ppm_v=0.4 WHERE id_equipo IN ('GNSS-SINOGNSS-MARS-PRO','GNSS-SINOGNSS-T300PLUS','GNSS-LEICA-GS16','GNSS-LEICA-GS18T','GNSS-LEICA-GS18');
-- Anteriormente las columnas genéricas de estos equipos contenían estático largo.
UPDATE base_evaluacion SET static_horizontal_mm=3,static_vertical_mm=5,static_ppm_h=0.5,static_ppm_v=0.5 WHERE id_equipo IN ('GNSS-LEICA-GS16','GNSS-LEICA-GS18T','GNSS-LEICA-GS18');
UPDATE base_evaluacion SET static_horizontal_mm=2.5,static_vertical_mm=5,static_ppm_h=0.5,static_ppm_v=0.5 WHERE id_equipo='GNSS-SINOGNSS-T300PLUS';
COMMIT;
