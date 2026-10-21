# Auditoría de software de oficina — 21 de octubre de 2026

El catálogo actualizado está en `catalogo_2026-10-21.json`. La migración 27 completa funciones documentadas sin sustituir valores desconocidos por «No». La migración 26 se conserva como historial.

## Evidencia incorporada

- **Compass Solution:** el manual ComNav V2.0.1 confirma Windows, ajuste por mínimos cuadrados, RINEX 2.0/3.0 en el selector de importación, DXF y CSV de resultados PPK. Se contrastó el manual inglés local con la [copia del manual del fabricante publicada por KPN](https://kpn.com.uy/web/wp-content/uploads/2017/12/Compass-Solution_User-Manual_V2.0_Espa%C3%B1ol.pdf). Sus capítulos 2.2, 3.1.4, 3.2 y 4 documentan importación, ajuste, PPK y exportación. El manual limita datos brutos dinámicos a ComNav y requiere dongle para PPK. La disponibilidad de funciones en una instalación concreta depende de versión y licencia.
- **PProcessing:** la [ficha oficial, revisión 03-03-2023](https://www.singularxyz.com/uploads/files/202506/7f0e2c99c04a5b2883575f5edef93573.pdf), página 2, confirma Windows, RINEX 2.x/3.x, ajuste de redes, DXF/CSV e informes HTML. La salida de imágenes UAV no demuestra por sí sola geotag EXIF.
- **Emlid Studio:** el [historial oficial](https://docs.emlid.com/emlid-studio/reference/changelogs/) documenta RINEX 2.11/3.03 y navegación 2.x/3.x; la versión 1.10 añade 3.04 **al convertidor**, sin certificar todos los modos. El [flujo Stop & Go](https://docs.emlid.com/emlid-studio/stop-n-go-with-ef-workflow/) genera CSV corregido a partir del CSV de Flow. Esto no equivale a exportación CAD genérica.

Las casillas RINEX 2/3 indican soporte documentado de esas familias, no compatibilidad con cada revisión o cualquier combinación de marcas. CSV también tiene un alcance específico por programa, explicado en su ficha.

## Datos pendientes

No se confirmó macOS, geotag ni gratuidad para Compass/PProcessing. Tampoco ajuste de redes, DXF ni informes equivalentes de ajuste para Emlid Studio. Estos campos siguen pendientes; no se inventaron capacidades para completar celdas.

## Recomendaciones

Una comparación general no produce un ganador universal por cantidad de datos confirmados. Compass y PProcessing tienen funciones principales documentadas en común; la calidad o precisión relativa requiere ensayos comparables. Las afirmaciones sobre copias, exempleados u origen empresarial no están acreditadas por estas fuentes técnicas y no puntúan.

Se conserva el contexto entre turnos sin mostrar automáticamente un conjunto cuando se pide solo GNSS. En conjuntos se asignan controladoras de la misma marca. Para Emlid se muestra Emlid Flow en teléfono compatible según su [documentación de conexión](https://docs.emlid.com/reachrs3/es/before-you-start/connecting-to-reach/); el teléfono no se considera incluido ni cumple automáticamente requisitos de una colectora dedicada.

Validación: pruebas de regresión, API con base configurada e IA simulada, compilación TypeScript/Vite y revisión visual de fichas a 1440 y 390 px. Los mensajes de espera describen el tema de la consulta; no simulan pasos internos completados por el proveedor.
