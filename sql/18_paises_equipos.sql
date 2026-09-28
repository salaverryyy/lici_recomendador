BEGIN;

ALTER TABLE equipos ADD COLUMN IF NOT EXISTS pais_marca TEXT;
ALTER TABLE equipos ADD COLUMN IF NOT EXISTS pais_fabricacion TEXT;

-- CHCNAV fue fundada y mantiene su sede y producción de receptores en Shanghái.
UPDATE equipos
SET pais_marca = 'China', pais_fabricacion = 'China'
WHERE marca = 'CHCNAV';

-- Emlid Tech Kft. está registrada en Budapest; Emlid confirma que diseña en
-- Hungría y fabrica estos receptores en China.
UPDATE equipos
SET pais_marca = 'Hungría', pais_fabricacion = 'China'
WHERE marca = 'Emlid';

-- Las etiquetas reglamentarias de GS16 y GS18 indican Made in Switzerland.
UPDATE equipos
SET pais_marca = 'Suiza', pais_fabricacion = 'Suiza'
WHERE marca = 'Leica';

-- SingularXYZ publica su sede y línea de producción en Shanghái.
UPDATE equipos
SET pais_marca = 'China', pais_fabricacion = 'China'
WHERE marca = 'SingularXYZ';

-- SinoGNSS es la marca de ComNav Technology, fabricante de receptores en
-- su parque industrial de Shanghái.
UPDATE equipos
SET pais_marca = 'China', pais_fabricacion = 'China'
WHERE marca = 'SinoGNSS';

-- South Surveying & Mapping Technology fabrica en Guangzhou, China.
UPDATE equipos
SET pais_marca = 'China', pais_fabricacion = 'China'
WHERE marca = 'South';

-- Trimble es estadounidense. El R8s del catálogo fue ensamblado en México;
-- CBP determinó que el país de origen del R12i es Estados Unidos.
UPDATE equipos
SET pais_marca = 'Estados Unidos', pais_fabricacion = 'México'
WHERE id_equipo = 'GNSS-TRIMBLE-R8S';

UPDATE equipos
SET pais_marca = 'Estados Unidos', pais_fabricacion = 'Estados Unidos'
WHERE id_equipo = 'GNSS-TRIMBLE-R12I';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM equipos
        WHERE NULLIF(BTRIM(pais_marca), '') IS NULL
           OR NULLIF(BTRIM(pais_fabricacion), '') IS NULL
    ) THEN
        RAISE EXCEPTION 'Hay equipos sin país de marca o de fabricación';
    END IF;
END $$;

ALTER TABLE equipos ALTER COLUMN pais_marca SET NOT NULL;
ALTER TABLE equipos ALTER COLUMN pais_fabricacion SET NOT NULL;

COMMIT;
