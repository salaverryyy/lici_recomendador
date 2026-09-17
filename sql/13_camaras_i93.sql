-- La ficha i93_DS_EN.pdf declara cámaras de 2 MP y 5 MP.
-- Corregir el dato omitido sin modificar requisitos ni pesos.
BEGIN;
UPDATE base_evaluacion SET cantidad_camaras = 2
WHERE id_equipo = 'GNSS-CHCNAV-I93' AND cantidad_camaras IS NULL;
COMMIT;
