# Recomendador: criterios y pesos en revision

Estos son los pesos propuestos por el usuario. Son un borrador y todavia no se han insertado en `reglas_recomendacion`.

| Criterio | Peso |
| --- | ---: |
| Necesita IMU | 15 |
| Necesita camara | 8 |
| Multifrecuencia | 4 |
| Numero minimo de canales | 5 |
| Precision minima estatico | 0 |
| Precision minima RTK | 6 |
| Precision RTK PPM | 2 |
| Precision estatico PPM | 2 |
| Memoria | 3 |
| SIM 4G | 5 |
| Laser | 8 |
| Bateria intercambiable | 4 |
| Bateria en caliente | 4 |
| MP de camara | 3 |
| Radio frecuencia | 5 |
| Constelaciones | 4 |
| Autonomia bateria | 5 |
| Peso | 3 |
| Dimensiones | 1 |
| Horizontal RTK | 5 |
| Vertical RTK | 5 |
| Tiempo inicializacion | 4 |

La suma inicial era 126; al retirar `Aplicacion` y `Trabajo sin base` por decision del usuario queda 101 en el borrador original. Puede usarse como escala relativa, pero el porcentaje debe dividir por la suma de los pesos **seleccionados** en el formulario, nunca por una suma fija:

`porcentaje = 100 * suma(peso_seleccionado * cumplimiento) / suma(peso_seleccionado)`

Todos los equipos permanecen en el ranking, incluso cuando no cumplen un requisito del formulario. Un criterio booleano incumplido aporta cero puntos en ese criterio; la respuesta debe marcar el incumplimiento de forma visible. Si no hay ningun criterio con peso positivo seleccionado, la respuesta muestra los cumplimientos e incumplimientos sin inventar un porcentaje.

`Aplicacion` y `Trabajo sin base` quedan descartadas por decision del usuario. `Multifrecuencia` significa varias bandas GNSS, pero el catalogo actual no registra bandas por equipo: `equipo_radio_frecuencia` registra frecuencias de radio y no sirve para calcular este criterio. No debe activarse hasta agregar un dato verificable sobre bandas GNSS.

La precision RTK aparece en varios criterios relacionados; hay que evitar que el mismo dato sume varias veces sin una razon explicita. `Precision minima estatico` con peso cero no influye en el ranking y, si se selecciona sola, no permite calcular porcentaje. La precision estatica queda poco representada en el borrador. La necesidad de camara y los MP, o la bateria intercambiable y el cambio en caliente, tambien requieren reglas que eviten premiar dos veces la misma capacidad.

El sistema debe explicar cada resultado con el valor del equipo, el umbral pedido, la puntuacion y el motivo de incumplimiento cuando corresponda. Los valores ausentes no equivalen a `No` salvo que la fuente lo confirme.

## Propuesta provisional para el MVP

El peso solo expresa importancia relativa cuando el usuario selecciona varios criterios. Si selecciona uno solo, su peso se cancela al normalizar y el cumplimiento de ese criterio decide la puntuacion. La propuesta siguiente no se ha insertado en PostgreSQL y requiere una prueba con consultas reales antes de fijarse.

| Criterio puntuado | Peso sugerido |
| --- | ---: |
| Tiene IMU | 10 |
| Tiene camara | 8 |
| Canales GNSS minimos | 5 |
| RTK horizontal mm | 6 |
| RTK vertical mm | 6 |
| RTK ppm horizontal | 2 |
| RTK ppm vertical | 2 |
| Estatico horizontal mm | 6 |
| Estatico vertical mm | 6 |
| Estatico ppm horizontal | 2 |
| Estatico ppm vertical | 2 |
| Memoria GB | 3 |
| SIM 4G | 5 |
| Laser | 8 |
| Bateria intercambiable | 4 |
| Bateria en caliente | 4 |
| Camara MP minimos | 3 |
| Radio UHF compatible | 5 |
| Constelaciones minimas | 4 |
| Autonomia minima horas | 5 |
| Peso maximo gramos | 3 |
| Dimensiones maximas mm | 1 |
| Tiempo maximo de inicializacion segundos | 2 |

Suma provisional: 102. Los campos genericos `Precision minima RTK` y `Precision minima estatico` se conservan, si hacen falta, como preguntas del formulario que se traducen a umbrales horizontal/vertical; no suman otro peso. `Multifrecuencia` queda suspendida hasta registrar bandas GNSS por equipo. Para evitar puntuaciones artificialmente altas, un campo de camara MP solo se evalua si el equipo tiene camara, y bateria en caliente solo si existe la capacidad correspondiente. Estos pesos son un punto de partida para comparar resultados, no un optimo demostrado.
