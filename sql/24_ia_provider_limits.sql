-- Gemini administra la cuota. Licitex deja de limitar solicitudes por visitante.
BEGIN;

DROP TABLE IF EXISTS ia_solicitudes;

-- Libera estados antiguos creados cuando cualquier 429 bloqueaba todo el servicio.
UPDATE ia_estado_servicio
SET cuota_hasta=NULL, ultimo_codigo=NULL, motivo=NULL, actualizado_en=NOW()
WHERE id=TRUE;

COMMIT;
