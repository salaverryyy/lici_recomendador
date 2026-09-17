BEGIN;
-- Se conserva el ID histórico para mantener referencias y enlaces existentes.
UPDATE equipos SET modelo='GS18I', descripcion='Receptor GNSS Leica GS18I con cámara y posicionamiento visual' WHERE id_equipo='GNSS-LEICA-GS18';
UPDATE base_evaluacion SET temperatura_operacion_min_c=-40, temperatura_operacion_max_c=65,
    temperatura_camara_min_c=-30, temperatura_camara_max_c=50,
    temperatura_almacenamiento_min_c=-40, temperatura_almacenamiento_max_c=85,
    humedad_max_pct=100, proteccion_ip='IP66 | IP68', caida_m=2,
    caida_condiciones='Vuelco desde jalón sobre superficies duras',
    vibracion_norma='ISO9022-36-08 | MIL-STD-810G 514.6 Cat.24',
    choque_condiciones='40 g / 15–23 ms; MIL-STD-810G 516.6 I',
    ambiental_notas='Con cámara: -30 a +50 °C; sin cámara: -40 a +65 °C. IP: IEC60529; MIL-STD-810G CHG-1 510.6 I, 506.6 II, 512.6 I. Humedad: ISO9022-13-06, ISO9022-12-04; MIL-STD-810G CHG-1 507.6 II.',
    ambiental_fuente='Extracto aportado el 2026-09-16; usuario confirma que el registro GS18 corresponde a GS18I el 2026-09-17.'
WHERE id_equipo='GNSS-LEICA-GS18';

-- Brochure SingularXYZ SFAIRA ONE PLUS, versión 17-10-2025.
INSERT INTO equipos (id_equipo,marca,modelo,categoria,descripcion,publicado)
VALUES ('GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS','SingularXYZ','Sfaira ONE Plus','GNSS',
        'Receptor GNSS compacto para RTK mediante CORS/NTRIP y conexión Bluetooth al teléfono.',TRUE)
ON CONFLICT (id_equipo) DO NOTHING;
INSERT INTO base_evaluacion (id_equipo,tiene_imu,canales_gnss,autonomia_bateria,peso_max,
    rtk_horizontal_mm,rtk_vertical_mm,rtk_ppm_h,rtk_ppm_v,
    static_horizontal_mm,static_vertical_mm,static_ppm_h,static_ppm_v,
    largo_mm,ancho_mm,alto_mm,gps,glonass,galileo,beidou,qzss,navic_irnss,sbas,constelaciones,
    ppp_h_cm,ppp_v_cm,tiene_ppp,temperatura_operacion_min_c,temperatura_operacion_max_c,
    temperatura_almacenamiento_min_c,temperatura_almacenamiento_max_c,proteccion_ip,caida_m,
    caida_condiciones,ambiental_notas,ambiental_fuente)
VALUES ('GNSS-SINGULARXYZ-SFAIRA-ONE-PLUS',TRUE,1408,16,409,
    8,15,1,1,2.5,5,0.5,0.5,50,50,149,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,6,
    5,10,TRUE,-45,75,-55,85,'IP65',1.5,'Diseñado para sobrevivir caída sobre concreto',
    'Humedad no especificada. Dimensiones cilíndricas: diámetro 50 mm y altura 149 mm. Autonomía: 16 h en transmisión Bluetooth y RTK según tabla eléctrica. Los 5 s son inicialización de IMU, no tiempo de encendido.',
    'Brochure SingularXYZ SFAIRA ONE PLUS GNSS RECEIVER, versión 17-10-2025, PDF aportado por el usuario.')
ON CONFLICT (id_equipo) DO NOTHING;
COMMIT;
