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
Top N sigue limitando cantidad de equipos y puede cortar un grupo empatado;
los puestos se calculan antes del corte.
