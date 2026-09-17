BEGIN;
-- Imagen de ficha técnica identificada por el usuario como CHCNAV i50, 2026-09-17.
UPDATE base_evaluacion SET
    temperatura_operacion_min_c = -40,
    temperatura_operacion_max_c = 65,
    temperatura_almacenamiento_min_c = -40,
    temperatura_almacenamiento_max_c = 75,
    proteccion_ip = 'IP67',
    ambiental_notas = 'Inmersión temporal hasta 1 m. Humedad y choque no legibles en la imagen aportada.',
    ambiental_fuente = 'Imagen de ficha técnica aportada por el usuario; modelo CHCNAV i50 confirmado el 2026-09-17. URL y revisión pendientes.'
WHERE id_equipo = 'GNSS-CHCNAV-I50';
COMMIT;
