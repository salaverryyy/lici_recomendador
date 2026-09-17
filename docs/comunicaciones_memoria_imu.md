# Comunicaciones, almacenamiento y constelaciones

La migración 12 añade 25 columnas a `base_evaluacion` y carga especificaciones
de las 23 fichas aportadas (incluido Sfaira). `tecnicas_datos.json` conserva cada
archivo de origen, los valores y las condiciones. Se actualiza memoria instalada
cuando la ficha declara una capacidad diferente; otros valores históricos se conservan.
Los valores no declarados permanecen NULL. Ejecutar la migración como carga inicial,
no volver a ejecutarla sobre modificaciones manuales posteriores.

## Recomendador

GPS, GLONASS, Galileo, BeiDou, QZSS, NavIC/IRNSS y SBAS tienen casillas independientes.
Solo los marcados participan; no se excluyen equipos. El contador antiguo sigue
disponible en la API por compatibilidad, pero no en el formulario. SBAS no se suma
al contador derivado de constelaciones del catálogo.

Memoria de fábrica suficiente: cumple sin condición adicional. Si es insuficiente,
se usa `memoria_expandida_max_gb` solo cuando `memoria_expandible` es verdadero.
Si alcanza, cuenta todos los puntos y se explica «Memoria (con memoria extendida)».
El detalle mantiene la memoria de fábrica y señala la ampliación necesaria; no se
pretende que el equipo venga con ella instalada. Si la ampliación tampoco alcanza,
el equipo no cumple y obtiene puntuación proporcional. Si no se conoce el máximo,
solo se evalúa la capacidad instalada conocida. No se suman almacenamiento interno
y tarjeta externa cuando la ficha no confirma una capacidad agregada.

Capacidades opcionales de fábrica (`memoria_opcional_fabrica_max_gb`) se muestran
separadas: no se consideran ampliaciones confirmadas. T300+: 8 GB estándar y
16/32 GB al ordenar. P6H: ROM opcional y MicroSD son dos vías diferentes.
Jupiter: 4 GB estándar y ampliable hasta 32 GB. Orion/X1/X1 Lite: 8 GB y hasta 32 GB.
i93 revisión March 2026: 32 GB y expansión externa 128 GB.

La generación de IMU se compara como declaración exacta del fabricante, sin escala
universal entre marcas. Mars Pro declara tercera generación. AUTO-IMU se conserva
como tecnología; QUANTUM Generation III del T300+ describe su motor GNSS.
Las generaciones desconocidas quedan NULL y no se inventan a partir de frecuencia,
grados de inclinación ni número de ejes.

## Condiciones y formatos

Se distinguen Bluetooth/versiones, Wi-Fi/estándares, LTE integrado, UHF Tx/Rx,
modos y protocolos de radio, potencia máxima y ajuste, batería interna y extracción,
registro RINEX/versiones y formato propietario. Las condiciones se muestran en la
ficha y comparador y son editables en administración.

RINEX sin revisión no demuestra RINEX 3.x; RTCM 3.x tampoco lo demuestra. Salida
binaria no garantiza registro binario. Jupiter/Mars permiten conversión a RINEX
mediante software; la versión no está declarada. Compatibilidad de protocolos puede
limitarse a recepción o depender de firmware. Las radios opcionales o extraíbles
requieren comprobar la configuración del equipo ofrecido.

RS3 tiene LoRa 868/915 MHz Tx/Rx y UHF 410–470 MHz solo Rx con antena opcional.
Se añadió ese rango al catálogo; el criterio Tx/Rx puede cumplirse mediante LoRa,
por lo que debe revisarse el modo por banda para una licitación específica.
i73 revisión August 2020 declara UHF interna solo Rx. i73+ declara Tx/Rx con 0.5/1 W.
Jupiter no declara LTE integrado en el brochure aportado; no se asigna el 4G de la
controladora al receptor. Las licencias, versiones regionales y actualizaciones de
firmware indicadas en las fichas se conservan en las notas y necesitan verificación.

Los nuevos pesos son provisionales y se ajustan desde administración.

Los 22 PDFs nuevos se adjuntaron como fichas del catálogo local; se conservó el
Sfaira ya cargado. Los objetos se gestionan mediante `equipo_archivos` y aparecen
en la ficha pública de cada equipo. No se versionan los archivos binarios de uploads;
el almacenamiento persistente de producción se configura por separado según
`archivos_equipos.md`.
