# Especificaciones pendientes de identificar o incorporar

Datos aportados por el usuario el 16 de septiembre de 2026. No se trasladan
entre variantes de un modelo. Los valores originales en Celsius son la referencia;
las conversiones Fahrenheit inconsistentes del Jupiter no se utilizan.

## Sfaira One Plus (incorporado el 17 de septiembre)

- Operación: −45 a +75 °C; almacenamiento: −55 a +85 °C.
- IP65; diseñado para sobrevivir caída de 1,5 m sobre concreto.
- Humedad no especificada.
- Datos técnicos y ambientales cargados mediante `11_gs18i_sfaira.sql`, desde
  brochure versión 17-10-2025. La ficha se adjuntó al catálogo local.

## Leica GS18I (identidad confirmada el 17 de septiembre)

- Operación con cámara: −30 a +50 °C; sin cámara: −40 a +65 °C.
- Almacenamiento: −40 a +85 °C; humedad hasta 100%, condición no especificada.
- IP66 | IP68: IEC60529; MIL STD 810G CHG-1 510.6 I,
  506.6 II y 512.6 I.
- Vuelco desde jalón de 2 m sobre superficies duras.
- Vibración: ISO9022-36-08 | MIL STD 810G 514.6 Cat.24.
- Humedad: ISO9022-13-06 | ISO9022-12-04 | MIL STD 810G CHG-1 507.6 II.
- Choque funcional: 40 g / 15 a 23 ms, MIL STD 810G 516.6 I.
- El usuario confirma que su registro GS18 representa GS18I. Se corrigió el
  nombre y se conservaron el ID histórico y sus referencias mediante la migración 11.

## Imagen adjunta: CHCNAV i50, confirmado el 17 de septiembre

- Operación: −40 a +65 °C; almacenamiento: −40 a +75 °C.
- IP67; inmersión temporal hasta 1 m.
- El dato de humedad y el ensayo de choque están ocultos.
- Dimensiones visibles: 140 × 130 × 106 mm; esta carga se limita a datos ambientales.
- Datos ambientales cargados mediante `10_ambientales_i50.sql`.

## Criterio de carga

`09_especificaciones_ambientales.sql` amplía `base_evaluacion` y carga los 20 modelos
identificados existentes. La migración 10 añade i50, sumando 21 modelos con datos.
La migración 11 identifica GS18I e incorpora Sfaira: 23 modelos con datos ambientales. No modifica
pesos, dimensiones ni autonomía a partir de estos extractos: pueden describir
configuraciones y modos de uso diferentes. No se inventan porcentajes de humedad
para los Emlid ni temperaturas de almacenamiento ausentes.

`ambientales_datos.json` conserva los datos cargados. La fuente está marcada como
extracto aportado por el usuario; faltan URL y revisión de las fichas para trazabilidad.
Las normas de ensayo se conservan como texto, sin convertirlas en una certificación
general MIL-STD-810. IP66 e IP68 se conservan juntos cuando ambos se declaran.

Estos campos están disponibles para lectura, edición administrativa y comparación.
El recomendador admite ahora temperatura operativa y de almacenamiento, humedad,
condensación, códigos IP aceptados, altura de caída y versión MIL-STD del ensayo
de vibración. Los pesos iniciales son provisionales y editables en administración.
Temperaturas: cumplimiento binario de cada extremo solicitado. Si se requiere
cámara, se aplica el rango restringido declarado, cuando existe. IP: coincidencia
con cualquiera de los códigos aceptados, sin inferir códigos no declarados.
Vibración: revisión exacta F/G/H, sin presumir equivalencia ni certificación global.
Humedad y caída mantienen el cálculo gradual de mínimos. Superficie y condiciones
de caída requieren revisión de la ficha. Datos faltantes puntúan cero y se explican
como `sin_datos`; no se descartan equipos.

Administración dispone de `/admin/tablas`: consulta paginada y protegida de
equipos, base_evaluacion, equipo_radio_frecuencia, equipo_archivos y reglas_recomendacion.
Las tablas de cuentas, sesiones y recuperación no están disponibles en esa vista.
