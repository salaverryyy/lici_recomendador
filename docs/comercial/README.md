# Configuraciones, conectividad y referencias comerciales — 21-10-2026

## Alcance de la revisión

`lte_sim_2026-10-21.json` registra los 33 equipos publicados (GNSS, controladoras y SLAM). Se revisaron las fichas técnicas aportadas y documentación adicional del fabricante. `sim_fisica` se mantiene separado de `lte_4g`: RS2 tiene SIM pero 3.5G; RS2+ y RS3 sí tienen LTE. «Leica 4G» dentro de formatos de corrección no acredita telefonía LTE. Si no se confirma una SIM física, no se presume ni presencia ni ausencia, y el requisito conjunto no obtiene puntos por internet compartido.

- [Jupiter, manual oficial](https://www.comnavtech.com/uploads/download/Jupiter%20Laser%20RTK%20User%20Guide.pdf): páginas PDF 17 y 45 describen SIM dentro del receptor y red 4G; página 33, memoria interna 8 GB y opciones 16/32 GB. La ficha anterior declara 4 GB: se conserva la capacidad histórica y se muestra la configuración interna de fábrica bajo pedido como condición. Cotecmi confirma expresamente que puede suministrar 8 GB internos bajo pedido. Confirmar revisión, módem y configuración de cada oferta.
- [T300 Plus, ficha oficial](https://www.comnavtech.com/uploads/soft/20240712/1aaddd430a35f816e2d5447e51da06be.pdf): ranura SIM y módem propio.
- [X1, fabricante](https://singularxyz.com/uploads/files/202506/ff4b35c2c65fcb985d6c2dc98875d7ec.pdf): SIM y módem 4G en X1, no en X1 Lite.
- [RS2/RS2+, documentación Emlid](https://docs.emlid.com/reachrs2/firmware-update/connecting-reach-to-the-internet/enabling-cellular-modem/) y [RS3](https://docs.emlid.com/reachrs3/specifications/specs/): SIM física y diferencias entre módems.
- [i93, fabricante](https://chcnav.com/uploads/i93_DS_EN.pdf): Nano-SIM y módem LTE integrado.

Los SLAM no reciben LTE por utilizar un móvil como pantalla, ni por tener GNSS/RTK. Cuando las fuentes no lo publican, quedan pendientes. Las referencias por modelo y documentos revisados constan en el JSON, sin convertir falta de documentación en una ausencia confirmada.

## Condiciones comerciales autorizadas por Cotecmi

La memoria interna opcional de fábrica puede cubrir un mínimo interno, con todos los puntos y condición visible «bajo pedido»; una tarjeta externa sigue sin cubrirlo. La capacidad estándar no se sustituye por la opcional ni se suman capacidades.

Se verificaron también las opciones internas de T20 (16/32 GB, nota 1 de su ficha), T300+ (16/32 GB, nota 5) y P6H (ROM 128 GB opcional, separado de MicroSD). Se elige la configuración publicada más pequeña que cubra el mínimo, por ejemplo 8 GB de Jupiter cuando se exigen 8 GB.

Cotecmi confirma disponibilidad de adaptador LEMO de 7 pines a USB-C **para carga y datos**. El catálogo marca esa alternativa comercial en los modelos con ese conector; no cambia el puerto nativo del fabricante. Cuenta todos los puntos para USB-C genérico y muestra el adaptador como condición. La compatibilidad y funciones para el modelo ofertado deben verificarse e incluirse. Una exigencia explícita de puerto USB-C nativo/directo usa `usb_c_nativo=true` y no se cubre con adaptación.

## Costos orientativos

`referencias_2026-10-21.json` conserva una entrada por equipo. No contiene costos internos de Cotecmi ni una cotización peruana. Solo precios públicos de unidades nuevas comparables en USD participan en el desempate; las monedas no convertidas, kits, usados, placeholders y casos sin precio no se tratan como cero. No se estiman flete, IGV, importación, licencias, accesorios ni ampliaciones.

Se contrastó la API pública de productos del distribuidor [Metricop](https://checkout.metricop.com/products.json?limit=250) con sus fichas. X1: USD 2,897.99; Orion ONE visual/láser: USD 3,528.99; X1 Lite: USD 2,014.99; Sfaira ONE Plus: USD 1,871.99. Los precios pueden variar por región o actualización. También se registran [RS3 oficial](https://emlid.com/reachrs3/) y [Z1 publicado por GNSS-vevo](https://www.gnss-vevo.hu/en/page/gnss-land-surveying-solution). Referencias de SinoGNSS en RUB y H1 en EUR quedan solo como documentación interna y no se mezclan con USD. Se excluyó el placeholder USD 99,999 de Jupiter y no se usaron anuncios genéricos que mezclan modelos.

El 21-10-2026 se contrastaron [Mars Pro](https://equipodetopografia.com/products/gnss-mars-pro-laser-rtk-sinognss), [Jupiter](https://equipodetopografia.com/products/gnss-jupiter-laser-rtk-de-sinognss) y [T20](https://equipodetopografia.com/products/gnss-t20-sinognss) en el mismo distribuidor mexicano, consultando también sus endpoints públicos `.js`. Se guardan importes originales y conversión común según [BCE](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml), fecha 21-10-2026: USD/EUR 1.1234 y MXN/EUR 20.7632. Solo se usa la oferta comercial: no se importan sus afirmaciones técnicas a la BD. No se afirma stock, precio peruano ni costo de la configuración con adaptador o memoria bajo pedido. La referencia individual publicada de Mars Pro es menor que la de Jupiter; ninguna regla fija esos modelos en un puesto.

Las referencias no se muestran en la interfaz, no se devuelven en la API pública y no se envían a Gemini. La ausencia de precio no demuestra que el equipo sea más caro. Orden: cumplimiento técnico y cobertura, preferencia comercial SinoGNSS en empate, costo comparable, año y criterio estable. La marca no aporta puntos técnicos y no puede adelantar a un equipo que cumple más. Las cotizaciones corresponden a Cotecmi.

## Imágenes de licitaciones

El chat acepta hasta tres JPG/PNG/WebP por mensaje, también pegadas desde el portapapeles. El navegador prepara imágenes de hasta 1 MB cada una, con máximo combinado de 2.4 MB para mantenerse bajo el límite del cuerpo de Vercel. El backend valida bytes, MIME real, dimensiones e imagen estática, y los envía como `inlineData` al [proveedor Gemini](https://ai.google.dev/api/generate-content). No se guardan archivos ni Base64 en el historial: quedan nombres y transcripción. La lectura y dudas se muestran por imagen; las dudas se agregan a revisión manual y no deben convertirse en valores inventados.

Se conserva el proveedor/modelos configurados; no se activa facturación ni otro servicio OCR. Las imágenes consumen la cuota del modelo. El historial visible no sustituye la revisión de los datos extraídos.

El inicio del asistente ofrece 30 ejemplos con una cola aleatoria local y tres sugerencias seleccionables, sin consumir IA. Cada grupo de ranking (GNSS, software o conjunto) se puede contraer. Las tarjetas usan la portada del catálogo o una foto de galería como miniatura cuando existe.
