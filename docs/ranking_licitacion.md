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
solicitados. Dentro de la igualdad técnica se usa `equipos.anio_modelo`
descendente; los años desconocidos quedan al final. A igual año se aplica la
preferencia comercial SinoGNSS solicitada por Cotecmi y finalmente el ID estable.
Esta preferencia no implica superioridad técnica ni concede puntos. Los equipos
empatados siguen compartiendo puesto. Un modelo anterior que cumple más queda
por encima de uno reciente que cumple menos.

El mismo orden se aplica al recomendador, al chat y a conjuntos GNSS–controladora–
software, conservando las condiciones técnicas y de marca del conjunto. El año
de modelo es metadato del catálogo, no una fecha exacta de lanzamiento; no se
rellenan años desconocidos con el año de una ficha o una actualización.

La memoria ampliada documentada conserva todos los puntos, igual que una
configuración opcional de fábrica cuando el mínimo es genérico. Las tarjetas,
opciones y ampliaciones no se suman entre sí ni se presumen instaladas/incluidas.
La condición aparece sin tener que abrir los detalles, además del valor de
fábrica y la capacidad evaluada. Una exigencia explícita de memoria instalada
mantiene `memoria_solo_fabrica=true` y no se cubre con estas opciones.
