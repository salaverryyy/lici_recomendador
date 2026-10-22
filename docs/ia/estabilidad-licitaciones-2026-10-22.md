# Estabilidad de interpretación y orden de conjuntos

## Causas comprobadas en el código

La puntuación es determinista para unos mismos requisitos, datos y pesos. La extracción previa era generativa: dos respuestas podían devolver distintos umbrales o ignorar criterios. Además, la composición ordenaba primero por ausencia de incumplimientos y después por porcentaje. Un conjunto con muchos datos pendientes podía superar a otro con más cumplimiento comprobado. Los dos ejemplos facilitados no contienen el identificador de modelo, por lo que no se puede atribuir retrospectivamente cada uno a un modelo concreto.

La cadena configurada por defecto es Gemini 3.8 Flash → 3.6 Flash → 3.5 Flash-Lite → 3.1 Flash-Lite; las variables de entorno pueden cambiarla. El respaldo se activa ante errores concretos de disponibilidad, cuota o respuesta inválida. No se elige un modelo por consulta ni se activa facturación.

## Correcciones

- Los pliegos GNSS estructurados con suficientes cláusulas reconocibles se normalizan desde el texto: canales, constelaciones, precisiones y ppm, IMU, almacenamiento, conectividad, formatos y condiciones ambientales. Los valores se leen del pliego, sin conocer candidatos ni usar valores estándar del catálogo. Las cláusulas no corroboradas se señalan para revisión y no generan puntos.
- Un pliego completo reemplaza las condiciones y selecciones heredadas del chat. Las preguntas breves y comparaciones conservan el flujo de conversación. La ruta de imágenes conserva la transcripción y validación de dudas; no se aplica automáticamente esta gramática al texto dudoso de una imagen.
- Se conserva +60 °C ante la alternativa escrita +60/+65 °C y se pide confirmar la ambigüedad. No se cambia a +65 por el estándar de un candidato.
- Los conjuntos se ordenan por porcentaje comprobado. En igualdad se revisan incumplimientos y pendientes antes del desempate comercial. Un dato desconocido no se convierte en cumplimiento. Los incumplimientos siguen visibles.
- Cada respuesta muestra arriba el modelo utilizado, si fue respaldo y los códigos que motivaron ese respaldo. Las tarjetas distinguen cumplimiento, incumplimiento y evaluación incompleta.

## Validación y límites

Pruebas con extracciones deliberadamente divergentes y con contexto previo producen la misma matriz y el mismo conjunto para el pliego de regresión. Se comprueban umbrales diferentes para evitar fijar los resultados del ejemplo y se verifica que mayor cumplimiento real prevalece sobre la preferencia de marca.

La comprobación local del caso reportado mantiene los incumplimientos documentados; no se cambian los datos para obtener una propuesta aprobada. El fixture versionado es sintético, con umbrales ficticios y sin copiar el documento del usuario. La media por familias sigue siendo una evaluación parcial, sin acreditar interoperabilidad, cantidades ofertadas ni cumplimiento total.

Esto reduce la variación en las cláusulas reconocidas; no promete que toda interpretación generativa sea idéntica. Las consultas libres, cláusulas no cubiertas, transcripciones y cambios de contexto requieren revisión. No se cachea una respuesta posiblemente errónea para aparentar consistencia.

## Fuentes oficiales revisadas

- [Google: Gemini 3.6 Flash y 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/generate-content/whats-new-gemini-3.6): usos y niveles de razonamiento predeterminados distintos. Los modelos recientes no admiten los antiguos controles de muestreo; no se añade una temperatura fija como supuesta garantía de consistencia.
- [Google: salidas estructuradas](https://ai.google.dev/gemini-api/docs/structured-output): el esquema valida la estructura JSON; la aplicación debe validar el significado y los requisitos extraídos.

No se añaden modelos de pago ni se cambia la configuración de facturación.
