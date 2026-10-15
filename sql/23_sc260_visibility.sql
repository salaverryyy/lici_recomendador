-- Garantiza que la controladora Cotecmi SingularXYZ SC260 esté publicada y
-- disponible para catálogo, recomendadores y contexto de IA.
BEGIN;

INSERT INTO equipos (
  id_equipo, marca, modelo, categoria, pais_marca, pais_fabricacion,
  descripcion, anio_modelo, publicado
) VALUES (
  'SINGULARXYZ-SC260', 'SingularXYZ', 'SC260', 'Controladora', 'China', 'China',
  'Controladora de campo Android con teclado QWERTY, pantalla táctil y conectividad 4G.',
  2025, TRUE
)
ON CONFLICT (id_equipo) DO UPDATE SET
  marca=EXCLUDED.marca,
  modelo=EXCLUDED.modelo,
  categoria=EXCLUDED.categoria,
  pais_marca=EXCLUDED.pais_marca,
  pais_fabricacion=EXCLUDED.pais_fabricacion,
  descripcion=EXCLUDED.descripcion,
  anio_modelo=EXCLUDED.anio_modelo,
  publicado=TRUE;

INSERT INTO controladora_especificaciones (
  id_equipo, sistema_operativo, android_version, procesador, cpu_nucleos,
  cpu_ghz, ram_gb, almacenamiento_gb, expansion_gb, pantalla_pulgadas,
  resolucion_ancho_px, resolucion_alto_px, pantalla_tactil, teclado_qwerty,
  botones_programables, bateria_mah, autonomia_h, carga_h, carga_rapida,
  camara_mp, lte_4g, bluetooth, bluetooth_version, wifi, wifi_estandar,
  nfc, usb_c, usb_otg, proteccion_ip, temperatura_operacion_min_c,
  temperatura_operacion_max_c, temperatura_almacenamiento_min_c,
  temperatura_almacenamiento_max_c, largo_mm, ancho_mm, alto_mm,
  bandas_celulares, sim, sensores, software, notas, fuente
) VALUES (
  'SINGULARXYZ-SC260', 'Android', 11, '8 núcleos a 2.0 GHz', 8, 2,
  4, 64, 512, 5.45, 720, 1440, TRUE, TRUE, 1, 9000, 18, 4, TRUE,
  13, TRUE, TRUE, '5.0', TRUE, 'IEEE 802.11 a/b/g/n/ac, 2.4/5 GHz',
  TRUE, TRUE, TRUE, 'IP68', -20, 55, -40, 70, 221, 78, 16.5,
  'FDD-LTE B1/B2/B3/B4/B5/B7/B8/B12/B17/B20/B28; TDD B34/B38/B39/B40/B41; WCDMA B1/B2/B5/B8; GSM B2/B3/B5/B8',
  '1 nano SIM; 1 ranura compartida SIM/TF',
  'GPS/BDS/GLONASS; G-Sensor, luz, acelerómetro, NFC, flash LED, micrófono y altavoz',
  'Compatibilidad con software de campo de terceros; la ficha no declara una lista específica.',
  'Autonomía superior a 18 h con pantalla encendida. Táctil capacitiva de 5 puntos. Peso, brillo, caída, brújula y norma MIL no declarados; no se infiere Wi-Fi 6 ni certificación GMS.',
  'SC260 Data Collector, versión 26-08-2025, páginas 1-2; auditoría 2026-09-18.'
)
ON CONFLICT (id_equipo) DO UPDATE SET
  sistema_operativo=EXCLUDED.sistema_operativo,
  android_version=EXCLUDED.android_version,
  procesador=EXCLUDED.procesador,
  cpu_nucleos=EXCLUDED.cpu_nucleos,
  cpu_ghz=EXCLUDED.cpu_ghz,
  ram_gb=EXCLUDED.ram_gb,
  almacenamiento_gb=EXCLUDED.almacenamiento_gb,
  expansion_gb=EXCLUDED.expansion_gb,
  pantalla_pulgadas=EXCLUDED.pantalla_pulgadas,
  resolucion_ancho_px=EXCLUDED.resolucion_ancho_px,
  resolucion_alto_px=EXCLUDED.resolucion_alto_px,
  pantalla_tactil=EXCLUDED.pantalla_tactil,
  teclado_qwerty=EXCLUDED.teclado_qwerty,
  botones_programables=EXCLUDED.botones_programables,
  bateria_mah=EXCLUDED.bateria_mah,
  autonomia_h=EXCLUDED.autonomia_h,
  carga_h=EXCLUDED.carga_h,
  carga_rapida=EXCLUDED.carga_rapida,
  camara_mp=EXCLUDED.camara_mp,
  lte_4g=EXCLUDED.lte_4g,
  bluetooth=EXCLUDED.bluetooth,
  bluetooth_version=EXCLUDED.bluetooth_version,
  wifi=EXCLUDED.wifi,
  wifi_estandar=EXCLUDED.wifi_estandar,
  nfc=EXCLUDED.nfc,
  usb_c=EXCLUDED.usb_c,
  usb_otg=EXCLUDED.usb_otg,
  proteccion_ip=EXCLUDED.proteccion_ip,
  temperatura_operacion_min_c=EXCLUDED.temperatura_operacion_min_c,
  temperatura_operacion_max_c=EXCLUDED.temperatura_operacion_max_c,
  temperatura_almacenamiento_min_c=EXCLUDED.temperatura_almacenamiento_min_c,
  temperatura_almacenamiento_max_c=EXCLUDED.temperatura_almacenamiento_max_c,
  largo_mm=EXCLUDED.largo_mm,
  ancho_mm=EXCLUDED.ancho_mm,
  alto_mm=EXCLUDED.alto_mm,
  bandas_celulares=EXCLUDED.bandas_celulares,
  sim=EXCLUDED.sim,
  sensores=EXCLUDED.sensores,
  software=EXCLUDED.software,
  notas=EXCLUDED.notas,
  fuente=EXCLUDED.fuente;

COMMIT;
