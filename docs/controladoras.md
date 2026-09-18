# Controladoras

SC260 (SingularXYZ) y R60 (SinoGNSS) están registradas en `equipos` con categoría `Controladora`. Sus 48 características comunes se guardan en `controladora_especificaciones`, separadas de `base_evaluacion` GNSS.

La migración `sql/14_controladoras.sql` crea la tabla y carga los datos de las dos fichas. Es transaccional y conserva los registros existentes al repetirse. `scripts/preparar_controladoras.py` genera este SQL para revisión, sin conectarse a la base de datos.

El administrador permite editar cada característica y consultar la tabla. Para añadir una nueva característica estructurada, ampliar los metadatos de `backend/app/controladoras.py` y crear una migración para su columna. Los detalles libres pueden guardarse en condiciones y observaciones.

El ranking evalúa exclusivamente las controladoras publicadas. Cada requisito indicado tiene el mismo peso provisional: cumple o no cumple; un dato ausente no suma puntos y aparece como «Sin información». «No lo necesito» omite un requisito booleano. Los límites numéricos muestran si son mínimos o máximos. IP y versiones Bluetooth se comparan exactamente, sin inferir equivalencias. La puntuación no sustituye la revisión de las bases de una licitación.

Cada consulta GNSS o de controladoras conserva requisitos y resultados en el navegador. Se puede cambiar con botones, pestañas o deslizando la barra de consultas.

Fuentes: SC260 Data Collector, versión 26-08-2025; SinoGNSS R60 Data Collector, Ver.2022.08.02. Los campos no declarados quedan nulos. La R60 declara cinco horas de carga en la primera página y hasta cuatro en la segunda: el tiempo queda vacío y la contradicción consta en observaciones. Las autonomías de 18+ h (SC260, pantalla encendida) y 30+ h (R60, condiciones sin especificar) conservan sus condiciones; no se equiparan protocolos de ensayo.
