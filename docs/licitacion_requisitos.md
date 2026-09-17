# Revisión de la licitación proporcionada en tres capturas

Las capturas describen un conjunto de 1 base y 2 rover, además de controladores GPS.
El ranking actual evalúa modelos individuales, mantiene todos los equipos y calcula ajuste
parcial. Un porcentaje alto no certifica cumplimiento íntegro del conjunto.

## Requisitos que ya pueden trasladarse al formulario

| Requisito | Campo actual | Valor |
|---|---|---|
| Canales mínimos | Canales GNSS mínimo | 450 |
| IMU | IMU | Sí |
| Memoria de 6 a 10 GB | Memoria mínima | 6 GB; falta máximo si 10 es obligatorio |
| Autonomía | Autonomía mínima | 5 h |
| Estático horizontal | Máximo mm / ppm | 3 mm / 0,1 ppm |
| Estático vertical | Máximo mm / ppm | 3,5 mm / 0,4 ppm |
| RTK horizontal | Máximo mm / ppm | 8 mm / 0,5 ppm |
| RTK vertical | Máximo mm / ppm | 15 mm / 0,5 ppm |
| Módem LTE | SIM 4G | Aproximación; no confirma por sí solo módem LTE integrado |

Los ppm horizontal y vertical ahora son independientes. Los clientes antiguos pueden seguir
enviando un valor compartido. La memoria de 32 GB y RAM de 4 GB de la sección controlador no
corresponden al almacenamiento del receptor.

## Datos pendientes para una evaluación completa

- Separar precisión estática de observaciones largas y estática rápida. Las cifras actuales
  no tienen ese detalle: comprobar el modo en la ficha antes de trasladarlas al formulario.
- Constelaciones requeridas por nombre: GPS, GLONASS, Galileo y BeiDou. Pedir cuatro constelaciones
  no garantiza esa combinación; ahora pueden consultarse individualmente en el comparador.
- Bandas por constelación (GPS L1/L2/L5 y GLONASS L1/L2/L3). No inferirlas por «multifrecuencia».
- Temperaturas, humedad y condiciones de ensayo, grados IP admitidos y ensayos MIL-STD-810.
- Bluetooth, WiFi, puertos, módem LTE integrado y funciones base/rover/estático sin controlador.
- Fecha de fabricación de las unidades ofrecidas: el año del modelo no determina antigüedad.
- Configuración del conjunto: 1 base, 2 rover, controladores compatibles, baterías y cargadores,
  estuches y alimentación 220 V/50 Hz.
- Catálogo separado de controladores con sistema operativo, teclado/pantalla, RAM, almacenamiento
  instalado/expandible, altavoz, batería, protección ambiental y conectividad.

Primero ampliar el modelo de datos con campos y fuentes documentadas. Después, un chat podrá
convertir texto en este mismo formulario estructurado, mostrar su interpretación y señalar
información faltante. El chat contextual no se implementó en esta etapa.

## Cámaras y protocolo

- Jupiter: dos cámaras y SNLongLink confirmados en la ficha oficial Ver.2026.04.03.
  https://www.comnavtech.com/uploads/soft/20260610/65c3a18ed92de20fc7d6004e92e5852f.pdf
- Orion ONE: una cámara descrita por SingularXYZ; SNLongLink sin verificar.
  https://www.singularxyz.com/product_detail/Orion_ONE
- Mars Pro: también documenta SNLongLink; no es exclusivo del Jupiter.
  https://www.comnavtech.com/product/receiver/marspro.html

Cantidad de cámaras tiene peso provisional 6 y SNLongLink peso 5, editables por administración.
Solo participan al solicitarse. Pedir dos cámaras concede 100% de ese criterio a dos cámaras y
50% a una; datos desconocidos se identifican como tales. Jupiter no se coloca primero automáticamente
si incumple otros requisitos elegidos. Los megapíxeles no se multiplican por cantidad de cámaras.
