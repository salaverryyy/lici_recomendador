# Corrección de rangos por componente y lectura de imágenes

Se revisaron los campos térmicos de los 26 GNSS publicados. Solo dos registros tenían límites específicos de cámara: Jupiter y Leica GS18 I. La atribución de Jupiter era errónea; la de GS18 I está declarada expresamente en su ficha y se conserva.

| Equipo / función | Operación en °C | Evidencia |
|---|---|---|
| Jupiter, receptor GNSS | −40 a +65 | Especificaciones ambientales. |
| Jupiter, láser | −20 a +50 | Bloque Especificaciones Láser. Estos límites estaban cargados incorrectamente como cámara. |
| Jupiter, cámara | Sin rango separado publicado en la ficha revisada | No se aplica el rango del láser al pedir cámara; se conserva el rango ambiental general del receptor. |
| Orion ONE, receptor | −40 a +65 | Tabla ENVIRONMENTAL. No se inventan límites separados para cámara o láser. |
| Leica GS18 I, con cámara | −30 a +50 | La ficha diferencia explícitamente operación con cámara y sin cámara. |
| Leica GS18 I, sin cámara | −40 a +65 | Tabla ambiental de la misma ficha. |

La migración 31 mueve los límites de Jupiter al componente correcto. No cambia temperaturas de otros receptores ni elimina la restricción genuina de GS18 I. Los campos desconocidos del láser se etiquetan como pendientes o no aplicables; no se rellenan con el rango general.

El evaluador combina el rango general únicamente con las funciones exigidas. La evaluación muestra el límite solicitado, el aplicado y su alcance. Si se exige usar el láser, se conserva su restricción. Las preguntas térmicas del chat se responden con estos mismos campos, diferenciando operación y almacenamiento.

También se corrige una omisión de lectura: «doble cámara» exige una cantidad mínima de dos y no solo presencia. Orion ONE declara un sensor visual de 2 MP; Jupiter declara dos cámaras de 2 MP. El láser o una función AR no aumentan la cantidad de cámaras. La aceptación contractual de equivalencias requiere validación de la entidad; no se deduce de que un producto haya ganado una licitación.

Los límites térmicos legibles de una transcripción se conservan aunque el modelo los omita o cambie. Si la lectura declara dudas sobre esos límites, no se convierten en criterios puntuables. Las pruebas versionadas usan fragmentos sintéticos, sin publicar la licitación ni sus capturas.

## Adjuntos

Se admiten hasta diez imágenes, seleccionadas o pegadas. El navegador reparte el presupuesto de tamaño entre las páginas, ajustando también adjuntos anteriores si se añaden más. Se conservan el límite total de 2,4 MB binarios, los formatos admitidos y la validación real del contenido. La petición incluye todas las imágenes y la respuesta debe incluir una lectura por cada una. El presupuesto de salida aumenta con el número de páginas; no se habilita facturación ni otro proveedor.

## Fuentes

- [Ficha oficial Jupiter](https://www.comnavtech.com/uploads/soft/20250415/424636fc51274f14ead63b6ac83be845.pdf). Contrastada visualmente con `SinoGNSS Jupiter Laser RTK_ESP.pdf`, versión 2025.08.06, página 1: rango ambiental arriba y rango láser inmediatamente antes del bloque de cámara.
- [Ficha oficial y especificaciones Orion ONE](https://www.singularxyz.com/Orion_ONE.html). Contrastada visualmente con `_Orion ONE GNSS Receiver (3).pdf`, versión 04-03-2026, página 1. La revisión del alcance láser no forma parte de esta corrección.
- Ficha del fabricante `Leica_GS18I_DS.pdf`, revisión 10.25, página 2: límites explícitos con y sin cámara.
