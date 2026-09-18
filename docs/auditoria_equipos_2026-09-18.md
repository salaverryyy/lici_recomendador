# Auditoría de equipos — 18 de septiembre de 2026

Se contrastaron las 25 fichas locales con los datos registrados: 23 GNSS y 2 controladoras. La ficha aportada determina la revisión técnica; la web oficial complementa los años y aclara casos puntuales. No se mezclan especificaciones de versiones distintas. Un vacío significa dato no verificado, no ausencia de la prestación. Esta revisión no certifica la oferta ni la configuración física de una unidad.

## Resultado por equipo

| Equipo | Ficha y páginas | Observaciones y revisión pendiente |
|---|---|---|
| CHCNAV i50 | ficha_tecnica_GPS-CHC-GNSS-i50.pdf pp. 1–3 | Peso no legible/declarado en la tabla aportada: requiere confirmación. Kit de 2 receptores con 4 baterías: 2 incluidas por receptor. Autonomía celular hasta 10 h; UHF 5–7 h. LEMO 7 pines confirmado visualmente en p.3. |
| CHCNAV i73 | i73_DS_EN_Surveyour2.pdf pp. 2,4 | Ficha revisión agosto 2020. Rover RTK 12 h, estático hasta 15 h. IMU hasta 45° en p.2; no mezclar con i73+. |
| CHCNAV i73+ | i73+_DS_EN.pdf pp. 2,4 | Rover hasta 24 h; base UHF 10.5 h. Especificación 60° en tabla y precisión a 30° en texto. Señales con asterisco y salida 10 Hz sujetas a firmware. |
| CHCNAV i93 | i93_DS_EN.pdf pp. 1–4 | Ficha marzo 2026: 1892 canales, 9900 mAh, IP68 y rover sin cámara hasta 34 h; visual hasta 24 h. Confirmar que el equipo ofertado es esta revisión. 10 Hz, señales marcadas y PointSky dependen de firmware/servicio. Noticia oficial tiene fecha 2023 y texto 2022: año exacto pendiente. |
| Emlid Reach RS2 | Datasheet RS2 ENG web.pdf pp. 1–2 | Autonomía usada: modo rover RTK (RS2/RS2+ 16 h; RS3 con inclinación 18 h), no las 22 h de registro. ~5 s es convergencia RTK, no encendido. RS2 tiene módem 3.5G, no LTE. |
| Emlid Reach RS2+ | Datasheet-RS2+-ENG-web.pdf pp. 1–2 | Autonomía usada: modo rover RTK (RS2/RS2+ 16 h; RS3 con inclinación 18 h), no las 22 h de registro. ~5 s es convergencia RTK, no encendido. RS2 tiene módem 3.5G, no LTE. |
| Emlid Reach RS3 | RS3-Datasheet-UHF.pdf pp. 1–2 | Autonomía usada: modo rover RTK (RS2/RS2+ 16 h; RS3 con inclinación 18 h), no las 22 h de registro. ~5 s es convergencia RTK, no encendido. RS2 tiene módem 3.5G, no LTE. |
| Leica GS16 | Leica_Viva_GS16_GNSS_smart_antenna_DS.pdf pp. 1–2 | Ficha 11.17: 0.93 kg, módem 3.75G; no importar Wi-Fi/LTE de GS18. RINEX y constelaciones/licencias según versión; NavIC futura actualización. SmartLink PPP opcional, H 3 cm. Memoria microSD, no memoria interna. |
| Leica GS18I | Leica_GS18I_DS.pdf pp. 1–2 | GS18 I: 1.25 kg, altura 109 mm y cámara 1.2 MP. Con cámara -30 a +50 °C; sin cámara -40 a +65 °C. PPP y radio según variante/servicio. NavIC L1 y otras señales futuras. Memoria hasta 4 GB y SD extraíble. |
| Leica GS18 T | Leica GS18 T BRO.pdf pp. 1–2 | Ficha octubre 2025, lanzamiento del modelo 2017. 1.23 kg, altura 109 mm, autonomía típica hasta 8 h. PPP y radio según variante/servicio. Memoria hasta 4 GB y SD extraíble. |
| SingularXYZ Orion ONE | _Orion ONE GNSS Receiver (3).pdf pp. 1–2 | Inicialización RTK <5 s, no encendido. Rango IMU 60°. La expansión de memoria es capacidad soportada, no instalada. No inferir baterías de repuesto. Serie con variantes ONE, AR y Laser: confirmar cámara/AR en la unidad; ONE y Laser incluyen láser. |
| SingularXYZ Sfaira ONE Plus | _Sfaira ONE Plus GNSS Receiver (1).pdf pp. 1–2 | Inicialización RTK <5 s, no encendido. Rango IMU 60°. La expansión de memoria es capacidad soportada, no instalada. No inferir baterías de repuesto. |
| SingularXYZ X1 | X1 GNSS Receiver.pdf pp. 1–2 | Inicialización RTK <5 s, no encendido. Rango IMU 60°. La expansión de memoria es capacidad soportada, no instalada. No inferir baterías de repuesto. Catálogo oficial confirma batería integrada. Intercambio y cambio en caliente no declarados. UHF mejorada LoRa Tx/Rx; protocolo de otras marcas Rx o módulo normal opcional: confirmar variante. |
| SingularXYZ X1 Lite | X1 Lite GNSS Receiver.pdf pp. 1–2 | Inicialización RTK <5 s, no encendido. Rango IMU 60°. La expansión de memoria es capacidad soportada, no instalada. No inferir baterías de repuesto. Catálogo oficial confirma batería integrada. Intercambio y cambio en caliente no declarados. UHF mejorada LoRa Tx/Rx; protocolo de otras marcas Rx o módulo normal opcional: confirmar variante. |
| SingularXYZ Z1 | Z1 GNSS Receiver.pdf pp. 1–2 | Inicialización RTK <5 s, no encendido. Rango IMU 60°. La expansión de memoria es capacidad soportada, no instalada. No inferir baterías de repuesto. 15 km en condiciones óptimas con LoRa; no equivale a alcance garantizado con otra marca. |
| SinoGNSS Jupiter Laser RTK | SinoGNSS Jupiter Laser RTK_ESP.pdf pp. 1–2 | Láser y 2 cámaras de 2 MP; IMU hasta 120°. PPP B2b/HAS opcional. Puerto Tipo-C. Módem celular y batería intercambiable no declarados para el receptor en esta ficha; el 4G al pie de p.2 pertenece al R80. 15 km con SNLonglink ideal. |
| SinoGNSS Mars Pro Laser RTK | SinoGNSS Mars Pro Laser RTK.pdf pp. 1–2 | RTK de red y línea base separados. PPP mencionada sin precisión numérica. SNLonglink confirmado en página oficial actual, distinto a protocolos de ficha 2024. Cambio de baterías en caliente no declarado en ficha. Confirmar módulo UHF/4G ofertado. |
| SinoGNSS P6H Portátil | SinoGNSS P6H Portátil_ES.pdf pp. 1–2 | Cámaras trasera 13 MP y frontal 5 MP. La ficha no declara autonomía ni inicialización RTK: no mantener 20 h/5 s sin respaldo. ROM 128 GB opcional y microSD hasta 128 GB son opciones distintas. Año exacto de lanzamiento pendiente; no usar año de revisión de ficha. |
| SinoGNSS T300+ | SinoGNSS T300 Plus GNSS Receiver.pdf pp. 1–2 | Ficha revisión 2025; modelo anterior con actualización K8/IMU en 2022. 14 h típicas, dos baterías intercambiables en caliente. 32 GB es opción de fábrica. Alcance 15 km ideal SNLonglink. No declara precisión distinta para RTK en red. Año exacto de lanzamiento pendiente; no usar año de revisión de ficha. |
| South Galaxy G1 | ficha_Tecnica_Southern_Galaxy_G1.pdf pp. 1–2 | 1 kg con batería. Módulo estándar 220 canales; 555/965 opcionales. Sensor de inclinación 30° opcional, no IMU de 60° confirmada. No declara autonomía. Red H8/V15 +0.5ppm. Estático de observaciones largas H2.5/V5 +0.5ppm. |
| South Galaxy G6 | ficha_tecnica_South_Galaxy_G6.pdf pp. 1–2 | 1.44 kg con batería; 336 canales estándar, 965 opcionales. Hasta 50 Hz. PPP/RTX requiere suscripción. Tabla de sensor inclinación 30°, texto shake tilt sin límite: confirmar versión. Cambio en caliente no declarado. |
| Trimble R12i | 022516-511H_Trimble R12i GNSS Receiver.pdf pp. 1–4 | 1.12 kg con batería/radio/antena; 6 h Tx 0.5 W, 5.5 h Tx 2 W y 6.5 h Rx. Inicialización RTK 2–8 s. TIP precisión especificada hasta 40°. RTX H2/V3 cm con servicio. Módem según variante/región. |
| Trimble R8s | Datasheet-Trimble-R8s-GNSS-System-English-USL-Screen.pdf pp. 1–2 | 1.52 kg con batería/radio/antena; altura 104 mm incluidos conectores. Autonomía Rx5 h, Tx0.5 W2.5 h, celular4 h: se usa Rx5. Inicialización típicamente <8 s. GSM/3G opcional, no LTE. Sin declaración de Wi-Fi/USB en puertos: confirmar. |
| SingularXYZ SC260 | colectora/_SC260 Data Collector (2).pdf pp. 1–2 | Revisadas páginas 1–2, versión 26-08-2025: Android11, CPU2GHz, RAM4/ROM64, pantalla5.45, 18 h pantalla encendida, IP68. Peso, caída, brújula y norma MIL no declarados. |
| SinoGNSS R60 | colectora/SinoGNSS R60 Data Collector (1).pdf pp. 1–2 | Revisadas páginas 1–2, versión 02-08-2022: Android12, RAM4/ROM64, pantalla5.5, 30+ h, IP67, caída1.6m, brújula electrónica. Carga: texto5 h frente a tabla≤4 h; se mantiene desconocida hasta confirmar. CPU GHz no declarada. |

## Años de lanzamiento

| Equipo | Año | Fuente primaria |
|---|---|---|
| Emlid Reach RS2 | 2019 | [Fuente oficial](https://blog.emlid.com/multi-band-reach-rs2-is-here/) |
| Emlid Reach RS2+ | 2022 | [Fuente oficial](https://blog.emlid.com/the-new-reach-rs2plus-with-lte/) |
| Emlid Reach RS3 | 2023 | [Fuente oficial](https://blog.emlid.com/ten-years-of-emlid-company-from-crowdfunding-to-survey-grade-rtk-gnss-solutions/) |
| Leica GS16 | 2016 | [Fuente oficial](https://leica-geosystems.com/pl-pl/page-archive/events/intergeo-2016/unused-pages/latest-innovations) |
| Leica GS18I | 2020 | [Fuente oficial](https://leica-geosystems.com/es-es/products/gnss-systems/smart-antennas/leica-gs18-t/the-leica-gs18-series-gnss-rtk-rovers-from-benchmark-to-better-than-ever) |
| Leica GS18 T | 2017 | [Fuente oficial](https://leica-geosystems.com/es-es/products/gnss-systems/smart-antennas/leica-gs18-t/the-leica-gs18-series-gnss-rtk-rovers-from-benchmark-to-better-than-ever) |
| SingularXYZ Orion ONE | 2024 | [Fuente oficial](https://www.singularxyz.com/news_detail/29) |
| SingularXYZ Sfaira ONE Plus | 2023 | [Fuente oficial](https://www.singularxyz.com/news_detail/47) |
| SingularXYZ X1 | 2023 | [Fuente oficial](https://www.singularxyz.com/news_detail/55) |
| SingularXYZ X1 Lite | 2023 | [Fuente oficial](https://www.singularxyz.com/news_detail/55) |
| SingularXYZ Z1 | 2024 | [Fuente oficial](https://www.singularxyz.com/news_detail/28) |
| SinoGNSS Jupiter Laser RTK | 2025 | [Fuente oficial](https://www.linkedin.com/posts/comnav-technology-ltd-_sinognss-comnavtech-surveying-activity-7363875120890716160-N7SN) |
| SinoGNSS Mars Pro Laser RTK | 2023 | [Fuente oficial](https://www.linkedin.com/posts/comnav-technology-ltd-_sinognss-comnavtech-surveying-activity-7363875120890716160-N7SN) |
| Trimble R12i | 2020 | [Fuente oficial](https://help.fieldsystems.trimble.com/trimble-access-release-notes/en/2020.10.htm) |
| Trimble R8s | 2015 | [Fuente oficial](https://www.nikon-trimble.co.jp/info/index.html?kind=3&newslist=71) |
| SingularXYZ SC260 | 2025 | [Fuente oficial](https://www.singularxyz.com/news_detail/116) |
| SinoGNSS R60 | 2022 | [Fuente oficial](https://www.comnavtech.com/about/news/256.html) |

Para i50, i73, i73+, i93, G1, G6, P6H y T300 Plus se buscaron anuncios del fabricante; el año exacto que no pudo corroborarse queda pendiente. El año 2022 existente del i73+ es compatible con el manual y documentación de 2022, pero se conserva como dato pendiente de anuncio primario. En i93 el anuncio oficial contradice 2022 en su texto y 2023 en encabezado/URL. P6H ya se exhibía en INTERGEO 2024: se retira el 2025 sin atribuir un lanzamiento exacto. T300 Plus ya existía antes de la revisión 2025 y el K8/IMU se actualizó en 2022: se retira 2025 sin mezclar versión y lanzamiento.

## Adaptaciones a las cuatro licitaciones

| Requisito | Tratamiento |
|---|---|
| RTK con radio y RTK de red en una misma licitación | Seleccionar Línea base y usar campos adicionales RTK en red. mm y ppm por eje, sin sustituir un modo por otro. |
| Estático 3 mm + 0.1 ppm / 3.5 mm + 0.4 ppm | Modo Observaciones largas; no confundir con estático rápido. |
| IMU 30° o 60° y salida 10/20 Hz | Nuevos umbrales independientes. 200 Hz de IMU no son 200 Hz de salida GNSS. Datos condicionados a firmware quedan pendientes. |
| Dos o tres baterías entregadas por receptor | Nuevo campo de baterías incluidas por receptor. No equivale a baterías que usa el equipo ni a cantidad total del kit. Confirmar la oferta. |
| USB, USB-C, RS-232 | Requisitos independientes. Si dice USB y/o RS-232, marcar solo la alternativa que el pliego admite; no convertir OR a AND. |
| L1/L2/L3/L5 y señales específicas por constelación | Verificación manual de tabla de señales y asteriscos de firmware. L3 de GLONASS no implica GPS L3. No se automatiza equivalencia ambigua. |
| Alcance radio 5 km en condiciones normales | Verificación de protocolo, terreno, potencia y ensayo. Un máximo ideal 15 km no garantiza 5 km normal. |
| IP67 o superior y MIL-STD-810F/G | Seleccionar códigos aceptados declarados. Una revisión MIL posterior no garantiza los mismos ensayos; IP68 no implica ensayo IP66. |
| Controladora RAM/ROM/pantalla/autonomía/caída | Mantener criterios existentes; añade brújula electrónica. SC260 5.45 y R60 5.5 no cumplen una exigencia de 6 pulgadas. |
| Batería, garantía, accesorios, capacitación, software de la misma marca, licencia perpetua y radio externa | Revisión de oferta/kit por separado; no inferir cumplimiento desde el receptor. |

## Cambios y fuentes adicionales

El archivo JSON contiguo registra los cambios por campo con valor previo y nuevo. Las observaciones quedan también en la ficha pública/admin. Se mantienen los valores numéricos que coinciden con las fichas; se corrigen diferencias comprobadas y se retiran valores sin respaldo cuando afectan al ranking. Las prestaciones opcionales requieren confirmar su compra/activación.

- [Mars Pro actual: SNLonglink](https://www.comnavtech.com/product/receiver/marspro.html)
- [X1 serie: batería integrada](https://singularxyz.com/uploads/files/202506/63b820627066b28ca866bc407441dcaa.pdf)
- [T300/T300 Plus: cronología y diferencias](https://www.comnavtech.com/about/blogs/368.html)
- [P6H exhibido en 2024](https://comnavtech.com/News_details/609.html)
- [i93 anuncio con fechas contradictorias](https://geospatial.chcnav.com/about/news/2023/chcnav-introduces-the-i93-imu---rtk-gnss-receiver-enhanced-with-the-vision---based-positioning)

Las bandas normalizadas usadas por el ranking también se corrigen: i73 430–470 MHz y G1 410–470 MHz. RS3 admite inclinación de 60° según la cronología oficial de Emlid enlazada arriba. Las opciones de controladoras incluyen umbrales de las licitaciones (6 pulgadas, 12 h, caída 1.2 m), incluso si ningún equipo actual los cumple.
