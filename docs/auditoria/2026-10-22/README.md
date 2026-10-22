# Auditoría de formatos RINEX y campos pendientes — 22 de octubre de 2026

Se revisaron los 33 equipos publicados: 26 GNSS, tres controladoras y cuatro escáneres SLAM. Se incorporan 125 valores corroborados: 39 completan campos ya existentes y 86 documentan por separado el registro directo y la conversión RINEX. No se sustituyen valores técnicos existentes ni se mezclan revisiones de equipos.

Los cambios y sus fuentes están en [cambios.json](cambios.json). La revisión por equipo, incluidos los campos que continúan pendientes, está en [revision_catalogo.json](revision_catalogo.json). La migración solo completa valores nulos y añade evidencia; no convierte los datos desconocidos en «No».

## Registro y exportación RINEX

| Equipos | Evidencia y alcance |
|---|---|
| SinoGNSS Jupiter | El manual, secciones 3.3.3.2–3.3.3.3, permite seleccionar y descargar directamente RINEX 2.10 y 3.02 en WebUI. |
| SinoGNSS Mars Pro, T20, T300+ | Sus observaciones ComNav Binary pueden convertirse con CRU a RINEX 2.01/2.11 y 3.01/3.02/3.03/3.04. Esta evidencia no acredita registro directo de esas revisiones. |
| Emlid Reach RS2, RS2+, RS3 | Registro directo RINEX 3.03 configurado con Emlid Flow. Emlid Studio 1.10 añade conversión a 3.04; no se traslada esa versión al registro directo del receptor. RINEX 2.x queda pendiente de confirmación específica. |
| SingularXYZ X1 | Manual X1-Series: selección directa de XYZ/RINEX 3.02/3.04 y conversión con SingularXYZ Converter. No se presume RINEX 2.x. |
| SingularXYZ X1 Lite, Orion ONE, Z1 | Se conserva la compatibilidad 3.02/3.04 publicada. La ruta directa o de conversión se mantiene pendiente si no está acreditada específicamente. |
| Leica GS10, GS25, GS16, GS18 T, GS18 I | Leica Infinity Help v3.1.1 documenta importación MDB y exportación 2.11/3.02. Verificar archivo, versión y licencia. No se deduce una versión nativa del receptor. |
| Trimble R8s, R12i | La ayuda oficial documenta conversión T02/T04 a RINEX 2.10/2.11 y varias revisiones 3.x. Verificar Configuration Utility y archivo de entrada. |
| CHCNAV i50, i73, i73+, i93 | Las fichas declaran 2.11/3.02; no se deduce la modalidad de grabación por separado. |
| SinoGNSS P6H, SingularXYZ Sfaira ONE Plus y South G1/G6 | Sin evidencia específica suficiente para rellenar las versiones pendientes. La precisión estática, una placa común o un menú genérico no acreditan exportación en ese modelo. |

El ranking distingue compatibilidad/exportación de registro nativo. La conversión documentada suma el cumplimiento del formato y muestra una condición visible con el software necesario. Si el requisito exige registro directo, la conversión no lo satisface. Admitir una familia RINEX no garantiza cada una de sus revisiones; se conservan las versiones exactas y la necesidad de validar un archivo real.

## Otros campos y límites de la revisión

Se completa carga USB-C donde está declarada inequívocamente, enlace de Internet compartido donde el manual describe ese flujo y exportaciones LAZ/PLY/E57 del LS600 mediante RealEditor. La existencia del software no prueba que su licencia esté incluida. El adaptador LEMO–USB-C Cotecmi continúa siendo exclusivamente de datos, sin carga.

Se conservan pendientes los datos no publicados o contradictorios. La ficha R60 indica cinco horas de carga en el texto y hasta cuatro en la tabla. La web actual de Orion ONE describe una revisión láser distinta a la versión validada por Cotecmi; no se sobrescribe su alcance. No se atribuyen características de South G1/G6 con IMU a las versiones históricas del catálogo.

## Fuentes principales

- [ComNav: guía CRU, conversión RINEX](https://www.comnavtech.com/about/blogs/445.html).
- [ComNav: Jupiter Laser RTK User Guide](https://www.comnavtech.com/uploads/download/Jupiter%20Laser%20RTK%20User%20Guide.pdf).
- [SingularXYZ: manual X1 Series](https://singularxyz.com/download-file/19).
- [Emlid: registro Reach RS2/RS2+](https://docs.emlid.com/reachrs2/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/), [Reach RS3](https://docs.emlid.com/reachrs3/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/) y [cambios de Emlid Studio](https://docs.emlid.com/emlid-studio/reference/changelogs/).
- [Leica Infinity Help v3.1.1, manual del fabricante alojado por la Universidad de Lisboa](https://fenix.ciencias.ulisboa.pt/downloadFile/1126037345804184/Leica%20Infinity%20User%20Guide%20v3.1.1.pdf), páginas PDF 37 y 45.
- [Trimble: Convert to RINEX](https://help.fieldsystems.trimble.com/tbc/17261.htm).
- [ComNav: ficha LS600 actualizada](https://www.comnavtech.com/uploads/soft/20250811/4e5ae729a4210495ed99192713a313ce.pdf), página 2, RealEditor.

Las fuentes específicas, condiciones y referencias a fichas aportadas se conservan por campo. Para reproducir la propuesta se ejecuta `scripts/preparar_auditoria_rinex.py` sobre la instantánea original; una exportación posterior a la migración solo propondrá los valores que sigan vacíos.
