# Hoja RECOMENDADOR: lectura del Excel

Archivo leído: `bd_especs_receivers.xlsx`, hoja `RECOMENDADOR` (27 filas por 8 columnas).
La hoja de entradas no tiene fórmulas; los cálculos están en `RESULTADOS_RECOMENDADOR` y el
orden final en `RESULTADO_FINAL`. De las 740 fórmulas de resultados, 44 contienen `#REF!`.
El cálculo antiguo también suma el peso de un campo booleano si el formulario contiene `No`,
y da una gran bonificación para que algunos equipos salten por encima de otros. Esas reglas
no se copiaron: `No` significa «no lo necesito» y todos los equipos siguen en el ranking.

Se conservaron los campos de entrada útiles: IMU, cámara, canales, RTK/estático horizontal y
vertical, ppm, radio, constelaciones, autonomía, memoria, SIM, láser, baterías, MP de cámara,
peso, dimensiones e inicio. Se retiraron aplicación, trabajo sin base y multifrecuencia según
las decisiones posteriores del usuario.

La hoja llama `RTK PPM máximo permitido (mm)` y `Estático PPM máximo permitido (mm)`;
el backend los etiqueta en ppm, mientras que los umbrales horizontal/vertical se miden en mm.
El selector de constelaciones del Excel permitía 7; ahora el máximo es 6 sin SBAS.
La radio se pide como mínimo y máximo MHz explícitos, para no confundir `868/915` con un
rango continuo. Las tres dimensiones se pueden dejar vacías por separado.

Las fórmulas del Excel se tomaron como referencia de los campos y del propósito, no como
una implementación fiable del ranking. El backend usa los datos PostgreSQL verificados y
explica cada puntuación.
