# Alta Emlid Reach RS4 estándar

Se incorpora `GNSS-EMLID-RS4` como equipo Emlid del catálogo Cotecmi. Se conserva la política de ecosistema: Emlid Flow en teléfono compatible y Emlid Studio para oficina; no se le asigna SC260, R60 o R80.

Fuente principal: ficha del fabricante aportada, `RS4 datasheet (LoRa & UHF) 2026.pdf`, tres páginas. La página 2 fue revisada visualmente para separar estático, PPK, RTK, autonomía e interfaces. La ficha se publica junto con la galería cuadrada y portada horizontal de estudio. Las imágenes son ilustraciones generadas basadas en las referencias, no fotografías documentales.

## Valores y condiciones relevantes

- Modelo estándar sin cámaras: no mezclarlo con Reach RS4 Pro. GNSS de 672 canales, hasta 10 Hz, 16 GB internos, LTE con nano-SIM, Wi-Fi y Bluetooth 5.1.
- RTK H 7 mm + 1 ppm, V 14 mm + 1 ppm. Estático H 4 mm + 0,5 ppm, V 8 mm + 1 ppm. PPK H 5 mm + 0,5 ppm y V 10 mm + 1 ppm se documenta por separado, sin usarlo como estático.
- 16 h como rover RTK con compensación; 22 h son registro de datos. Batería interna 5000 mAh / 36 Wh; carga y datos USB-C, carga PD. La oferta y los repuestos no se deducen de la batería del equipo.
- UHF integrada Tx/Rx 410–470 MHz hasta 2 W, TRIMTALK 450S/GMSK, más LoRa en bandas regionales. No equivale a soportar cualquier protocolo de radio. Configuración, antena, bandas y potencia dependen de la región.
- RINEX directo 3.03 documentado y respaldo UBX; conversión 3.04 con Emlid Studio 1.10. RINEX 2.x queda pendiente de verificación específica.
- Compensación IMU sin límite angular impuesto según Emlid. Se registra una declaración booleana y no un máximo numérico inventado. No es una garantía de precisión constante; la fórmula depende del ángulo y se requiere FIX.
- Operación −40 a +65 °C, IP68, 927 g. No se inventan normas MIL, caída, almacenamiento, ampliación de memoria, SBAS o correcciones PPP por no figurar en las fuentes específicas revisadas.
- Año de modelo 2025, de acuerdo con el anuncio del fabricante; «2026» identifica la ficha aportada. Hungría representa la sede actual de la marca según su página de contacto. El país de fabricación del RS4 debe verificarse en etiqueta o certificado, sin copiar el de otros modelos.

La evidencia de los 119 campos está en `emlid-rs4.json`; los valores no corroborados siguen pendientes. La migración 32 no sobrescribe una fila de RS4 existente o ediciones posteriores.

## Fuentes complementarias del fabricante

- [Producto Reach RS4](https://emlid.com/reachrs4/).
- [Puertos, radio y LTE](https://docs.emlid.com/reachrs4/specifications/specs/).
- [Registro y descarga RINEX/UBX](https://docs.emlid.com/reachrs4/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/).
- [Emlid Studio 1.10: L5 y RINEX 3.04](https://docs.emlid.com/emlid-studio/reference/changelogs/).
- [IMU: ausencia de límite angular impuesto, precisión y necesidad de inicialización](https://blog.emlid.com/imu-tilt-compensation-in-surveying/).
- [Presentación del RS4, RS4 Pro y RX2 el 6 de octubre de 2025](https://community.emlid.com/t/meet-the-new-rs4-rx2-and-rs4-pro/43631).
- [Sede de Emlid](https://emlid.com/contacts/).
