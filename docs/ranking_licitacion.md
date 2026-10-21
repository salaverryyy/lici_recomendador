# Revisión de la simulación

Entrada reproducible: `licitacion_simulada.json`. Antes de corregir datos,
i93, Orion ONE y Jupiter obtenían 91.26%. Ahora los empates comparten puesto;
su orden interno no significa que exista un ganador único.

La ficha i93_DS_EN.pdf declara dos cámaras (2 MP y 5 MP). Su cantidad estaba
en NULL: SQL 13 corrige la omisión. Con los pesos actuales pasa a 97.09%; Jupiter
conserva 91.26%. El i93 cumple todos los criterios que cumple Jupiter en esta
entrada y tiene además LTE integrado y RINEX 3.x documentados. Esos dos datos
de Jupiter siguen sin confirmar en su brochure. El 4G de la controladora no
demuestra 4G integrado en el receptor.

Ningún conjunto de pesos no negativos puede hacer que Jupiter supere al i93
con esta entrada y estos datos. Aumentar el peso de las cámaras tampoco:
ambos tienen dos. Se conservan pesos provisionales; hace falta conocer los
factores diferenciadores de la adjudicación, como oferta/configuración, precio
o requisitos adicionales. No se agregan bonificaciones por marca o modelo.

Láser y SNLongLink están sin preferencia en la captura y no participan. Pueden
seleccionarse si son requisitos reales. El estático vertical pedido es 2.5 mm
frente a 5 mm declarados por los tres; el documento compartido anteriormente
pedía 3.5 mm. Revisar cuál corresponde a la licitación efectiva.

Comprobación con el mismo formulario y añadiendo únicamente láser y SNLongLink:
Jupiter 92.24% (puesto 1), Orion 87.93%, i93 86.21%. Este resultado es una
prueba de sensibilidad, no una modificación de los requisitos de la captura.

Los NULL se explican como «Sin datos», no como ausencia confirmada. La memoria
extendible conserva puntos cuando cumple con ampliación y lo declara.
Top N incluye todos los equipos empatados en el puesto de corte.

## Orden de presentación — 21 de octubre de 2026

Primero se ordena por porcentaje de cumplimiento y cobertura de los criterios
solicitados. Dentro de la igualdad técnica se aplica primero la preferencia
comercial SinoGNSS; después el menor costo de mercado comparable en USD,
el año de modelo descendente y el ID estable. Un precio sin confirmar nunca es cero.
Esta preferencia no implica superioridad técnica ni concede puntos. Los equipos
empatados siguen compartiendo puesto. Un modelo anterior que cumple más queda
por encima de uno reciente que cumple menos.

Las referencias comerciales solo se usan en el servidor: se eliminan de la API
pública y del catálogo enviado a Gemini, y no se muestran en las tarjetas.
La falta de precio comparable no demuestra que el equipo sea más caro.
Mars Pro y Jupiter se contrastaron en el mismo distribuidor, con una conversión
común del BCE. El orden deriva de datos comerciales y no de IDs o del texto de una
licitación. Si cambia el cumplimiento (por ejemplo, alcance láser), se recalcula
antes de aplicar cualquier desempate.

Las preguntas concretas y comparaciones responden en modo conversacional, sin
recalcular rankings ni volver a mostrar el conjunto. Se conserva intacto el
contexto anterior para retomar posteriormente la licitación.

El botón de elección usa `/api/ia/seleccionar-gnss`, valida el catálogo permitido,
conserva requisitos y reconstruye el conjunto de la misma marca sin llamar a
Gemini. Retira selecciones incompatibles de otra marca y confirma la elección en
el historial y en las tarjetas. La selección permanece al recargar.

El mismo orden se aplica al recomendador, al chat y a conjuntos GNSS–controladora–
software, conservando las condiciones técnicas y de marca del conjunto. El año
de modelo es metadato del catálogo, no una fecha exacta de lanzamiento; no se
rellenan años desconocidos con el año de una ficha o una actualización.

La memoria ampliada documentada conserva todos los puntos, igual que una
configuración opcional de fábrica cuando el mínimo es genérico. Las tarjetas,
opciones y ampliaciones no se suman entre sí ni se presumen instaladas/incluidas.
La condición aparece sin tener que abrir los detalles, además del valor de
fábrica y la capacidad evaluada. Una exigencia explícita de memoria instalada
mantiene `memoria_solo_fabrica=true`: acepta una opción interna de fábrica
documentada bajo pedido, pero no tarjetas externas. Ver [configuraciones y
auditoría SIM/LTE](comercial/README.md).

## Corrección de carga y cobertura de requisitos

LEMO y el adaptador USB-C ofrecido por Cotecmi son solo de archivos. USB-C para
datos y carga por USB-C son criterios separados: el adaptador no satisface carga.
La migración 29 guarda la corrección y sus fuentes. No se presume carga por tener
un conector USB-C nativo.

Si se permite LTE integrado o compartido, ambas vías se representan en un único
criterio explícito, con condición visible cuando se depende de un enlace externo.
Este flujo debe estar documentado; Bluetooth/Wi-Fi no lo acreditan solos. Exigir
LTE integrado conserva la validación de módem y SIM propios.

El respaldo de extracción cubre condiciones explícitas de carga, LTE, caída,
vibración y RINEX 3.x. La aplicación común a receptores/colectoras se conserva
cuando el documento lo dice, aceptando las alternativas IP expresas. Las señales,
protocolos y certificaciones que aún no tienen evaluación suficiente quedan en
revisión manual. Una familia requerida ausente cuenta como cero en el promedio del
conjunto: no se elimina del denominador para favorecer una propuesta incompleta.
