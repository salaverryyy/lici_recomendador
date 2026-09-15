-- La columna id se genera sola. Este script se puede repetir sin duplicar rangos.
BEGIN;
INSERT INTO equipo_radio_frecuencia (id_equipo, frecuencia_min_mhz, frecuencia_max_mhz)
VALUES
    ('GNSS-SOUTH-G1', 403, 470),
    ('GNSS-SOUTH-G6', 403, 473),
    ('GNSS-CHCNAV-I50', 410, 470),
    ('GNSS-CHCNAV-I73', 410, 470),
    ('GNSS-CHCNAV-I73PLUS', 410, 470),
    ('GNSS-CHCNAV-I93', 410, 470),
    ('GNSS-TRIMBLE-R8S', 403, 473),
    ('GNSS-TRIMBLE-R12I', 403, 473),
    ('GNSS-LEICA-GS16', 403, 470),
    ('GNSS-LEICA-GS18', 403, 473),
    ('GNSS-LEICA-GS18T', 403, 473),
    ('GNSS-LEICA-GS18T', 902, 928),
    ('GNSS-EMLID-RS2', 868, 868),
    ('GNSS-EMLID-RS2', 915, 915),
    ('GNSS-EMLID-RS2PLUS', 868, 868),
    ('GNSS-EMLID-RS2PLUS', 915, 915),
    ('GNSS-EMLID-RS3', 868, 868),
    ('GNSS-EMLID-RS3', 915, 915),
    ('GNSS-SINGULARXYZ-X1', 410, 470),
    ('GNSS-SINGULARXYZ-X1-LITE', 410, 470),
    ('GNSS-SINGULARXYZ-ORION-ONE', 410, 470),
    ('GNSS-SINGULARXYZ-Z1', 410, 470),
    ('GNSS-SINOGNSS-MARS-PRO', 410, 470),
    ('GNSS-SINOGNSS-T300PLUS', 410, 470),
    ('GNSS-SINOGNSS-JUPITER', 410, 470)
ON CONFLICT ON CONSTRAINT radio_rango_unico DO NOTHING;
COMMIT;

-- Resultado esperado: 25.
SELECT COUNT(*) AS rangos_importados FROM equipo_radio_frecuencia;
