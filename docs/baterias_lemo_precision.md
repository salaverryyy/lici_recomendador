# Baterías, conectores y modos de precisión

Migración: `sql/15_baterias_lemo_precision.sql`. No confundir cantidad de bloques de batería del receptor con celdas internas ni repuestos incluidos en el kit. El i50 declara dos baterías intercambiables y cuatro en el kit (páginas 1–2). Mars Pro declara 2 × 3400 mAh y peso con dos baterías (p.1); T300 Plus declara dos baterías intercambiables (pp.1–2). Los demás valores de uno corresponden a una batería singular interna o extraíble descrita en la ficha. SingularXYZ no declara claramente cantidad y queda sin dato. El paquete opcional de cuatro del G1 no se incorpora como cantidad simultánea.

LEMO de 7 pines: R12i p.3, R8s p.2, i93 p.4, Mars Pro p.1, T300 Plus p.2, X1 y X1 Lite p.2. G1 pp.1–2 y G6 p.1 declaran LEMO de cinco pines y USB de siete: son conectores distintos. GS16, GS18T y GS18I p.2 mencionan LEMO sin cantidad de pines. Ausencia de declaración no se convierte en «No».

Mars Pro Ver.2024.03.14 p.1: RTK en red H 8 mm + 0.5 ppm, V 15 mm + 0.5 ppm; una sola línea base H 8 mm + 1 ppm, V 15 mm + 1 ppm. Estático rápido H 2.5 mm + 0.5 ppm, V 5 mm + 0.5 ppm; observaciones largas H 3 mm + 0.1 ppm, V 3.5 mm + 0.4 ppm.

R12i p.2, R8s p.2 y Leica p.2 también declaran el modo RTK en red H 8 mm + 0.5 ppm, V 15 mm + 0.5 ppm. T300 Plus p.2 no declara ese modo: se conserva RTK H 8 mm + 1 ppm, V 15 mm + 1 ppm. Se separan las observaciones largas de T300 Plus y Leica de los valores de estático rápido.

La API conserva el modo de línea base y estático rápido por defecto para clientes anteriores. El formulario permite seleccionar red y observaciones largas. Los mm y ppm mantienen criterios distintos; no se intercambian ni se toma la mejor cifra de modos diferentes. Los equipos sin declaración del modo seleccionado se muestran «Sin datos».
