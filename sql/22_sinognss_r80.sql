-- SinoGNSS R80 auditada contra la ficha técnica aportada por el usuario.
-- Los campos no declarados permanecen NULL y no se atribuyen al colector las
-- funciones IMU o láser que Survey Master ejecuta con receptores compatibles.
BEGIN;

INSERT INTO equipos (
  id_equipo, marca, modelo, categoria, pais_marca, pais_fabricacion,
  descripcion, anio_modelo, publicado
) VALUES (
  'SINOGNSS-R80', 'SinoGNSS', 'R80', 'Controladora', 'China', 'China',
  'Controladora de campo Android 12 con pantalla de 6 pulgadas, teclado QWERTY, 4G y batería de 9000 mAh.',
  2026, TRUE
)
ON CONFLICT (id_equipo) DO UPDATE SET
  marca=EXCLUDED.marca,
  modelo=EXCLUDED.modelo,
  categoria=EXCLUDED.categoria,
  pais_marca=EXCLUDED.pais_marca,
  pais_fabricacion=EXCLUDED.pais_fabricacion,
  descripcion=EXCLUDED.descripcion,
  anio_modelo=EXCLUDED.anio_modelo,
  publicado=EXCLUDED.publicado;

INSERT INTO controladora_especificaciones (
  id_equipo, sistema_operativo, android_version, procesador, cpu_nucleos,
  ram_gb, almacenamiento_gb, pantalla_pulgadas, resolucion_ancho_px,
  resolucion_alto_px, brillo_nits, pantalla_tactil, teclado_qwerty,
  teclado_retroiluminado, botones_programables, bateria_mah, autonomia_h,
  carga_rapida, camara_mp, autofocus, lte_4g, bluetooth,
  bluetooth_version, wifi, wifi_estandar, wifi_6, nfc, usb_c, usb_otg,
  proteccion_ip, temperatura_operacion_min_c, temperatura_operacion_max_c,
  temperatura_almacenamiento_min_c, temperatura_almacenamiento_max_c,
  caida_m, peso_g, largo_mm, ancho_mm, alto_mm, bandas_celulares, sim,
  sensores, software, notas, fuente
) VALUES (
  'SINOGNSS-R80', 'Android', 12, 'MediaTek de 8 núcleos (según tabla técnica)', 8,
  4, 64, 6, 720, 1440, 500, TRUE, TRUE, TRUE, 8,
  9000, 16, TRUE, 13, TRUE, TRUE, TRUE, '5.1', TRUE,
  'IEEE 802.11 a/b/g/n/ac, doble banda 2.4/5 GHz y roaming rápido', FALSE,
  TRUE, TRUE, TRUE, 'IP67', -25, 60, -40, 70, 1.5, 488,
  242, 87.6, 24,
  'GSM B2/B3/B5/B8; WCDMA B1/B2/B4/B5/B8; LTE-TDD B34/B38/B39/B40/B41; LTE-FDD B1/B2/B3/B4/B5/B7/B8/B12/B17/B19/B20/B25/B28A/B28B',
  '2 ranuras para tarjeta SIM',
  'NFC 13.56 MHz; teclado QWERTY, pad numérico y direccional; 2 botones laterales de toma de datos',
  'Survey Master: flujos base/rover, estático, PPK y RTK; replanteo de superficies y CAD; conversión ComNavBinary a RINEX; servicio en la nube.',
  'Autonomía declarada superior a 16 h; se registra 16 h como mínimo conservador. USB-C con OTG. La ficha no declara expansión de memoria, certificación GMS, frecuencia CPU ni brújula integrada. Se conserva MediaTek, indicado en la tabla técnica; la segunda página muestra un icono Qualcomm incompatible con esa tabla. Las funciones de medición visual con láser e inclinación IMU mostradas en Survey Master dependen del receptor conectado y no se atribuyen a la R80. La segunda página contiene además el encabezado erróneo “R50 Data Collector”, aunque portada, imágenes y especificaciones identifican el producto como R80.',
  'SinoGNSS R80 Data Collector_EN.pdf, Ver.2026.1.19, páginas 1-2; ficha aportada por el usuario el 2026-10-15.'
)
ON CONFLICT (id_equipo) DO UPDATE SET
  sistema_operativo=EXCLUDED.sistema_operativo,
  android_version=EXCLUDED.android_version,
  procesador=EXCLUDED.procesador,
  cpu_nucleos=EXCLUDED.cpu_nucleos,
  ram_gb=EXCLUDED.ram_gb,
  almacenamiento_gb=EXCLUDED.almacenamiento_gb,
  pantalla_pulgadas=EXCLUDED.pantalla_pulgadas,
  resolucion_ancho_px=EXCLUDED.resolucion_ancho_px,
  resolucion_alto_px=EXCLUDED.resolucion_alto_px,
  brillo_nits=EXCLUDED.brillo_nits,
  pantalla_tactil=EXCLUDED.pantalla_tactil,
  teclado_qwerty=EXCLUDED.teclado_qwerty,
  teclado_retroiluminado=EXCLUDED.teclado_retroiluminado,
  botones_programables=EXCLUDED.botones_programables,
  bateria_mah=EXCLUDED.bateria_mah,
  autonomia_h=EXCLUDED.autonomia_h,
  carga_rapida=EXCLUDED.carga_rapida,
  camara_mp=EXCLUDED.camara_mp,
  autofocus=EXCLUDED.autofocus,
  lte_4g=EXCLUDED.lte_4g,
  bluetooth=EXCLUDED.bluetooth,
  bluetooth_version=EXCLUDED.bluetooth_version,
  wifi=EXCLUDED.wifi,
  wifi_estandar=EXCLUDED.wifi_estandar,
  wifi_6=EXCLUDED.wifi_6,
  nfc=EXCLUDED.nfc,
  usb_c=EXCLUDED.usb_c,
  usb_otg=EXCLUDED.usb_otg,
  proteccion_ip=EXCLUDED.proteccion_ip,
  temperatura_operacion_min_c=EXCLUDED.temperatura_operacion_min_c,
  temperatura_operacion_max_c=EXCLUDED.temperatura_operacion_max_c,
  temperatura_almacenamiento_min_c=EXCLUDED.temperatura_almacenamiento_min_c,
  temperatura_almacenamiento_max_c=EXCLUDED.temperatura_almacenamiento_max_c,
  caida_m=EXCLUDED.caida_m,
  peso_g=EXCLUDED.peso_g,
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
