# Especificaciones pendientes de identificar o incorporar

Datos aportados por el usuario el 16 de septiembre de 2026. No se trasladan
entre variantes de un modelo. Los valores originales en Celsius son la referencia;
las conversiones Fahrenheit inconsistentes del Jupiter no se utilizan.

## Sfaira One Plus (no existe en el catálogo)

- Operación: −45 a +75 °C; almacenamiento: −55 a +85 °C.
- IP65; diseñado para sobrevivir caída de 1,5 m sobre concreto.
- Humedad no especificada.

## Leica GS18I (no existe en el catálogo; GS18 es otro modelo)

- Operación con cámara: −30 a +50 °C; sin cámara: −40 a +65 °C.
- Almacenamiento: −40 a +85 °C; humedad hasta 100%, condición no especificada.
- IP66 | IP68: IEC60529; MIL STD 810G CHG-1 510.6 I,
  506.6 II y 512.6 I.
- Vuelco desde jalón de 2 m sobre superficies duras.
- Vibración: ISO9022-36-08 | MIL STD 810G 514.6 Cat.24.
- Humedad: ISO9022-13-06 | ISO9022-12-04 | MIL STD 810G CHG-1 507.6 II.
- Choque funcional: 40 g / 15 a 23 ms, MIL STD 810G 516.6 I.

## Imagen adjunta (modelo no visible)

- Operación: −40 a +65 °C; almacenamiento: −40 a +75 °C.
- IP67; inmersión temporal hasta 1 m.
- El dato de humedad y el ensayo de choque están ocultos.
- Dimensiones visibles: 140 × 130 × 106 mm; no se cargan sin identificar modelo.

## Criterio de carga

`09_especificaciones_ambientales.sql` amplía `base_evaluacion` y carga los 20 modelos
identificados existentes. i50 y GS18 quedan sin datos ambientales. No modifica
pesos, dimensiones ni autonomía a partir de estos extractos: pueden describir
configuraciones y modos de uso diferentes. No se inventan porcentajes de humedad
para los Emlid ni temperaturas de almacenamiento ausentes.

`ambientales_datos.json` conserva los datos cargados. La fuente está marcada como
extracto aportado por el usuario; faltan URL y revisión de las fichas para trazabilidad.
Las normas de ensayo se conservan como texto, sin convertirlas en una certificación
general MIL-STD-810. IP66 e IP68 se conservan juntos cuando ambos se declaran.

Estos campos están disponibles para lectura, edición administrativa y comparación.
No alteran todavía la puntuación del recomendador; incorporar requisitos ambientales
requiere definir cómo evaluar cada rango y los ensayos solicitados.
