BEGIN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS carga_usb_c BOOLEAN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS lemo_solo_datos BOOLEAN;
ALTER TABLE base_evaluacion ADD COLUMN IF NOT EXISTS internet_compartido BOOLEAN;

-- Corrección expresa de Cotecmi: la alternativa comercial LEMO 7 pines es solo
-- para archivos. No convertir un conector ni un adaptador en capacidad de carga.
UPDATE base_evaluacion SET lemo_solo_datos=TRUE,
    baterias_conectores_notas=CONCAT_WS(' ',baterias_conectores_notas,'Corrección Cotecmi 21-10-2026: LEMO de 7 pines y adaptador USB-C solo archivos, sin carga. Batería extraíble recargada por separado.'),
    carga_usb_c=CASE WHEN usb_c IS NOT TRUE THEN FALSE ELSE carga_usb_c END
WHERE usb_c_con_adaptador IS TRUE AND lemo IS TRUE AND lemo_pines=7;

-- Manual Jupiter, apartado 2.5.2: alimentación/carga mediante Type-C.
UPDATE base_evaluacion SET carga_usb_c=TRUE, internet_compartido=TRUE
WHERE id_equipo='GNSS-SINOGNSS-JUPITER';
-- Ficha T20 suministrada: puerto USB-C con carga rápida.
UPDATE base_evaluacion SET carga_usb_c=TRUE WHERE id_equipo='GNSS-SINOGNSS-T20';
-- Manual Mars Pro del fabricante, 5.7 PDA CORS: Internet de controladora.
UPDATE base_evaluacion SET internet_compartido=TRUE WHERE id_equipo='GNSS-SINOGNSS-MARS-PRO';

INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota)
SELECT id_equipo,'lemo_solo_datos','True','https://licitex-omega.vercel.app/',
 'Corrección expresa Cotecmi: LEMO y adaptador de 7 pines solo archivos',
 'carga-enlace-2026-10-21','confirmado',
 'Sustituye la declaración anterior de carga y datos. Batería extraíble recargada por separado; adaptador no acredita carga USB-C.'
FROM base_evaluacion WHERE lemo_solo_datos IS TRUE
ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;

INSERT INTO equipo_dato_fuentes(id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,estado,nota)
VALUES
('GNSS-SINOGNSS-JUPITER','carga_usb_c','True','https://www.comnavtech.com/uploads/download/Jupiter%20Laser%20RTK%20User%20Guide.pdf','Manual Jupiter, 2.5.2','carga-enlace-2026-10-21','confirmado','Type-C charger y carga de batería explícitos.'),
('GNSS-SINOGNSS-JUPITER','internet_compartido','True','https://www.comnavtech.com/uploads/download/Jupiter%20Laser%20RTK%20User%20Guide.pdf','Manual Jupiter, 5.5.3 PDA CORS','carga-enlace-2026-10-21','confirmado','La controladora debe tener Internet; comprobar servicio LTE externo.'),
('GNSS-SINOGNSS-MARS-PRO','internet_compartido','True','https://fcc.report/FCC-ID/2ACHBMARSPRO/6887371.pdf','Manual Mars Pro del fabricante, 5.7 PDA CORS','carga-enlace-2026-10-21','confirmado','Controladora con Internet mediante SIM o Wi-Fi y enlace Bluetooth al receptor.')
ON CONFLICT(id_equipo,campo,fuente_url,version_fuente) DO NOTHING;
COMMIT;
