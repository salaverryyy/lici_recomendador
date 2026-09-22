BEGIN;

ALTER TABLE base_evaluacion
  ADD COLUMN IF NOT EXISTS laser_alcance_m NUMERIC(8,2)
  CHECK (laser_alcance_m >= 0);

CREATE TABLE IF NOT EXISTS equipo_dato_fuentes (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_equipo TEXT NOT NULL REFERENCES equipos(id_equipo) ON DELETE CASCADE,
  campo TEXT NOT NULL,
  valor_declarado TEXT NOT NULL,
  fuente_url TEXT NOT NULL DEFAULT '',
  documento TEXT NOT NULL DEFAULT '',
  version_fuente TEXT NOT NULL DEFAULT '',
  pagina TEXT,
  fecha_consulta DATE NOT NULL DEFAULT CURRENT_DATE,
  estado TEXT NOT NULL CHECK (estado IN ('confirmado','opcional','conflicto','no_verificado')),
  nota TEXT,
  UNIQUE (id_equipo, campo, fuente_url, version_fuente)
);

CREATE INDEX IF NOT EXISTS equipo_dato_fuentes_equipo_campo_idx
  ON equipo_dato_fuentes (id_equipo, campo);

CREATE TABLE IF NOT EXISTS ia_estado_servicio (
  id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
  cuota_hasta TIMESTAMPTZ,
  ultimo_codigo INTEGER,
  motivo TEXT,
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO ia_estado_servicio (id) VALUES (TRUE) ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS ia_solicitudes (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cliente_hash TEXT NOT NULL,
  creada_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ia_solicitudes_cliente_fecha_idx
  ON ia_solicitudes (cliente_hash, creada_en DESC);

-- El ángulo comparable es la inclinación máxima desde la vertical hacia un lado.
-- Los 120° publicitados para Jupiter representan el barrido total (±60°).
UPDATE base_evaluacion SET
  laser=TRUE, laser_alcance_m=10, inclinacion_imu_deg=60,
  lte_4g=FALSE, sim_4g=FALSE,
  auditoria_notas=CASE WHEN COALESCE(auditoria_notas,'') LIKE '%Corrección 2026-09-22:%'
    THEN auditoria_notas ELSE CONCAT_WS(' ', auditoria_notas,
    'Corrección 2026-09-22: láser 10 m según ficha técnica de la versión Orion ONE evaluada; sin módem 4G integrado declarado.') END
WHERE id_equipo='GNSS-SINGULARXYZ-ORION-ONE';

UPDATE base_evaluacion SET
  laser=TRUE, laser_alcance_m=50, inclinacion_imu_deg=60,
  lte_4g=FALSE, sim_4g=FALSE,
  auditoria_notas='Láser fijo de 50 m y dos cámaras de 2 MP. La ficha expresa 120° de barrido total: se registra 60° por lado para compararlo con los demás equipos. Memoria instalada 4 GB, ampliable según ficha. El 4G mostrado al pie de la ficha pertenece al R80, no al receptor Jupiter.'
WHERE id_equipo='GNSS-SINOGNSS-JUPITER';

UPDATE base_evaluacion SET
  laser=TRUE, laser_alcance_m=10, inclinacion_imu_deg=60,
  lte_4g=TRUE, sim_4g=TRUE,
  auditoria_notas=CASE WHEN COALESCE(auditoria_notas,'') LIKE '%Verificación 2026-09-22:%'
    THEN auditoria_notas ELSE CONCAT_WS(' ', auditoria_notas,
    'Verificación 2026-09-22: inclinación IMU 60°, láser 10 m y módem 4G integrado declarados por la página oficial.') END
WHERE id_equipo='GNSS-SINOGNSS-MARS-PRO';

UPDATE base_evaluacion SET lte_4g=FALSE, sim_4g=FALSE,
  auditoria_notas=CASE WHEN COALESCE(auditoria_notas,'') LIKE '%módem celular 3.5G%'
    THEN auditoria_notas ELSE CONCAT_WS(' ', auditoria_notas,
    'La ficha oficial declara módem celular 3.5G; no se contabiliza como 4G LTE.') END
WHERE id_equipo='GNSS-TRIMBLE-R12I';

UPDATE base_evaluacion SET lte_4g=FALSE, sim_4g=FALSE
WHERE id_equipo='GNSS-EMLID-RS2';
UPDATE base_evaluacion SET lte_4g=TRUE, sim_4g=TRUE
WHERE id_equipo IN ('GNSS-EMLID-RS2PLUS','GNSS-EMLID-RS3');

-- LTE significa módem 4G integrado en el receptor; no Wi-Fi a una controladora
-- ni módem 3G/3.5G. Los NULL se conservan cuando la variante no está confirmada.
UPDATE base_evaluacion SET lte_4g=FALSE, sim_4g=FALSE
WHERE id_equipo IN ('GNSS-CHCNAV-I73','GNSS-CHCNAV-I73PLUS','GNSS-LEICA-GS16',
                    'GNSS-SINGULARXYZ-X1-LITE','GNSS-SINGULARXYZ-Z1',
                    'GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS','GNSS-TRIMBLE-R8S');
UPDATE base_evaluacion SET lte_4g=TRUE, sim_4g=TRUE
WHERE id_equipo IN ('GNSS-CHCNAV-I50','GNSS-CHCNAV-I93','GNSS-LEICA-GS18',
                    'GNSS-LEICA-GS18T','GNSS-SINGULARXYZ-X1','GNSS-SINOGNSS-P6H',
                    'GNSS-SINOGNSS-T300PLUS','GNSS-SOUTH-G1','GNSS-SOUTH-G6');

INSERT INTO equipo_dato_fuentes
  (id_equipo,campo,valor_declarado,fuente_url,documento,version_fuente,pagina,estado,nota)
VALUES
('GNSS-SINGULARXYZ-ORION-ONE','laser_alcance_m','10 m','','_Orion ONE GNSS Receiver (3).pdf','ficha técnica evaluada','1–2','confirmado','Dato de la ficha aportada; corresponde a esta versión, aunque existan páginas comerciales de otras variantes.'),
('GNSS-SINGULARXYZ-ORION-ONE','lte_4g','No declarado integrado','','_Orion ONE GNSS Receiver (3).pdf','ficha técnica evaluada','1–2','confirmado','No se atribuye 4G sin declaración del fabricante para esta unidad.'),
('GNSS-SINOGNSS-JUPITER','laser_alcance_m','50 m','https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf','Jupiter Laser RTK','2026-06','1–2','confirmado','Alcance fijo declarado.'),
('GNSS-SINOGNSS-JUPITER','inclinacion_imu_deg','60° por lado','https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf','Jupiter Laser RTK','2026-06','1–2','confirmado','120° es el barrido total, equivalente a ±60°.'),
('GNSS-SINOGNSS-JUPITER','memoria','4 GB, ampliable','https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf','Jupiter Laser RTK','2026-06','2','confirmado','Se conserva la memoria instalada de la ficha; la ampliación no se suma a la capacidad instalada.'),
('GNSS-SINOGNSS-JUPITER','lte_4g','No integrado','https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf','Jupiter Laser RTK','2026-06','2','confirmado','La mención 4G de esa página corresponde a la controladora R80.'),
('GNSS-SINOGNSS-MARS-PRO','inclinacion_imu_deg','60°','https://www.comnavtech.com/product/receiver/marpro.html','Mars Pro Laser RTK','consulta 2026-09-22',NULL,'confirmado','Inclinación máxima desde la vertical.'),
('GNSS-SINOGNSS-MARS-PRO','lte_4g','Integrado','https://www.comnavtech.com/product/receiver/marpro.html','Mars Pro Laser RTK','consulta 2026-09-22',NULL,'confirmado','Módem 4G declarado.'),
('GNSS-SINGULARXYZ-X1','memoria','8 GB, ampliable hasta 32 GB','https://www.singularxyz.com/product_detail/X1','X1 GNSS Receiver','consulta 2026-09-22',NULL,'confirmado','8 GB es capacidad instalada; 32 GB es capacidad soportada.'),
('GNSS-SINGULARXYZ-X1','lte_4g','Integrado','https://www.singularxyz.com/product_detail/X1','X1 GNSS Receiver','consulta 2026-09-22',NULL,'confirmado','Red celular 4G declarada.'),
('GNSS-SINOGNSS-T300PLUS','memoria','8 GB; 16/32 GB de fábrica opcional','https://www.comnavtech.com/uploads/soft/20260130/8c492621bfc9b40c1e63a74a48b10706.pdf','T300 Plus','revisión 2025','2','opcional','La opción de fábrica no reemplaza el valor instalado por defecto.'),
('GNSS-SINOGNSS-T300PLUS','lte_4g','Configuración integrada disponible','https://www.comnavtech.com/uploads/soft/20260130/8c492621bfc9b40c1e63a74a48b10706.pdf','T300 Plus','revisión 2025','2','opcional','Confirmar la variante ofertada.'),
('GNSS-TRIMBLE-R12I','lte_4g','No: módem 3.5G','https://geospatial.trimble.com/en/products/hardware/trimble-r12i','Trimble R12i','consulta 2026-09-22',NULL,'confirmado','No debe puntuar como 4G LTE.'),
('GNSS-EMLID-RS2','lte_4g','No: módem 3.5G','https://docs.emlid.com/reachrs2/es/specifications/specs/','Reach RS2/RS2+ specifications','consulta 2026-09-22',NULL,'confirmado','La primera generación RS2 usa 3.5G.'),
('GNSS-EMLID-RS2PLUS','lte_4g','LTE','https://docs.emlid.com/reachrs2/es/specifications/specs/','Reach RS2/RS2+ specifications','consulta 2026-09-22',NULL,'confirmado','La versión RS2+ incorpora LTE.')
ON CONFLICT (id_equipo,campo,fuente_url,version_fuente) DO UPDATE SET
  valor_declarado=EXCLUDED.valor_declarado,
  documento=EXCLUDED.documento,
  pagina=EXCLUDED.pagina,
  fecha_consulta=CURRENT_DATE,
  estado=EXCLUDED.estado,
  nota=EXCLUDED.nota;

COMMIT;
