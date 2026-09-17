BEGIN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS cantidad_camaras INTEGER CHECK (cantidad_camaras >= 0);
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS tiene_snlonglink BOOLEAN;
-- Ausencia confirmada de cámara: cantidad cero. Presencia sola no permite inferir cantidad.
UPDATE base_evaluacion SET cantidad_camaras=0 WHERE tiene_camara=FALSE AND cantidad_camaras IS NULL;
-- Fuente: ficha oficial Jupiter Ver.2026.04.03:
-- https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf
UPDATE base_evaluacion SET cantidad_camaras=2, tiene_camara=TRUE, tiene_snlonglink=TRUE
WHERE id_equipo='GNSS-SINOGNSS-JUPITER';
-- Mars Pro también soporta el protocolo; no es exclusivo del Jupiter.
-- https://www.comnavtech.com/product/receiver/marspro.html
UPDATE base_evaluacion SET tiene_snlonglink=TRUE WHERE id_equipo='GNSS-SINOGNSS-MARS-PRO';
-- Cámara individual descrita por el fabricante del Orion ONE:
-- https://www.singularxyz.com/product_detail/Orion_ONE
UPDATE base_evaluacion SET cantidad_camaras=1, tiene_camara=TRUE
WHERE id_equipo='GNSS-SINGULARXYZ-ORION-ONE';
COMMENT ON COLUMN base_evaluacion.cantidad_camaras IS 'Cantidad física de cámaras; no se suma a los megapíxeles. NULL si no se conoce.';
COMMENT ON COLUMN base_evaluacion.tiene_snlonglink IS 'Compatibilidad documentada con SNLongLink; NULL si no está verificada.';
COMMIT;
