# Auditoría de catálogo y ranking — 20 de octubre de 2026

Se revisaron los 33 equipos del catálogo: 26 receptores GNSS, 3 controladoras y 4 escáneres SLAM, incluidos los equipos externos. Se contrastaron fichas aportadas y páginas/documentación del fabricante. El inventario detallado por equipo está en [catalogo.json](catalogo.json); la actualización aplicable está en [SQL 25](../../../sql/25_auditoria_integral.sql).

## Alcance y límites de la evidencia

La revisión registra 174 valores contrastados, normalizados o corregidos; esto no significa 174 celdas nuevas. También clasifica 496 campos pendientes y 122 campos no aplicables. Los pendientes incluyen especificaciones no publicadas, modos no desglosados por el fabricante y condiciones comerciales que dependen del kit. No se puede convertir una ausencia documental en un número, un cero o un «No» fiable. Por eso se mantienen valores técnicos nulos cuando corresponde, con explicación visible en ficha y comparador. No se afirma que el catálogo haya quedado sin incertidumbre técnica.

Cada cambio y cada campo sin dato de las tablas técnicas revisadas recibe evidencia en `equipo_dato_fuentes`, con documento, fuente, estado y nota. Una página comercial genérica sirve para identificar al fabricante; la ficha nombrada es la referencia técnica cuando no hay una página específica accesible. Las fuentes no son una certificación del kit ofertado ni de licencias incluidas. Cuando una web describe otra revisión, no se mezclan sus mejores especificaciones con la ficha aportada. Los campos ya poblados no se sustituyen indiscriminadamente por datos de revisiones diferentes.

La revisión visualiza las fuentes en la ficha del equipo. El comparador muestra «No aplica», «Depende del kit ofertado», «Modo no especificado por separado» o «No publicado / pendiente de confirmar» según corresponda. Estas etiquetas no entran como si fueran valores técnicos en el cálculo.

## Hallazgos relevantes

- **Mars Pro:** LEMO de 7 pines para serial; no equivale a USB-C. Se confirma RS-232. La ficha aportada declara 32 GB y la página actual 8 GB: se conserva 32 GB con advertencia de variante. Se mantienen 60° de inclinación por lado y láser de 10 m.
- **Jupiter:** USB-C confirmado y ensayo MIL-STD-810G Method 514.6 documentado. Memoria interna de fábrica de 4 GB: no cumple una exigencia de 8 GB internos instalados aunque admita ampliación. Láser de 50 m; 120° total se trata como 60° por lado.
- **T300+:** USB/serial mediante LEMO de 7 pines; no USB-C físico. Se distingue memoria instalada de opciones de fábrica al ordenar. RINEX 3.x nativo sigue pendiente si la fuente solo menciona RINEX sin versión.
- **T20:** autonomía corregida a 13 h según la ficha española aportada (2025.09.04), sin trasladar las 20 h de otra revisión. Frecuencia de posicionamiento 10 Hz, diferenciada del registro bruto.
- **Emlid RS2/RS2+/RS3:** RINEX 3.03 confirmado por la documentación de Emlid Flow. El conector de 9 pines no se etiqueta como LEMO. LoRa Tx/Rx de 868/915 MHz no demuestra Tx/Rx de 410–470 MHz; el RS3 dispone de recepción UHF en esta última banda, sin transmisión.
- **Leica GS10/GS25/GS16:** tarjeta extraíble de 8 GB no se presenta como memoria interna instalada; se agrega `memoria_es_interna` para distinguirlo en la evaluación estricta.
- **CHCNAV i50/i73:** i50 de la ficha oficial declara 1,29 kg y Mini-USB. i73 de la revisión aportada dispone de UHF receptor, no transmisor; no confundir con i73+.
- **R80/SC260:** expansión TF de R80 hasta 512 GB y brújula confirmadas; SIM+TF no significa doble SIM. SC260 con Wi-Fi ac no acredita Wi-Fi 6. CPU GHz, GMS y tiempos de carga sin publicación se mantienen pendientes.
- **SLAM:** LS600 conserva la configuración de 32 líneas/300 m, diferenciada de 16 líneas/120 m y de la precisión absoluta. No se dan por probados LAZ/E57/PLY por pertenecer al software de otro modelo. En H1, LAZ/DXF quedan pendientes, no «No». H2 declara GNSS opcional y alcance condicionado por reflectividad. HERON LITE sin cámara no se confunde con LITE Color: cámara 0, RGB no; USB-C del PDA no se atribuye al escáner.

Guías complementarias de Emlid: [RS2 — registro PPK](https://docs.emlid.com/reachrs2/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/) y [RS3 — registro PPK](https://docs.emlid.com/reachrs3/ppk-quickstart/how-to-record-and-download-logs/ppk-logging/).

## Método de ranking

El porcentaje principal GNSS pasa a **cumplimiento ponderado estricto**: suma de pesos de requisitos cumplidos / suma de pesos de requisitos seleccionados × 100. Cada mínimo incumplido o sin evidencia obtiene cero; cumplir obtiene todo su peso. La cercanía al umbral se conserva en `porcentaje_afinidad` como diagnóstico secundario y no decide puestos. Por ejemplo, 7,99 GB no cumplen un mínimo de 8 GB.

No se suman ventajas no pedidas. Más cámaras, mayor láser o más canales no desempatan si todos cumplen los mínimos seleccionados. El orden dentro de un empate solo estabiliza la lista y no declara un ganador. Se amplía el valor predeterminado de GNSS y chat a 20 equipos y se conservan todos los empatados en el último puesto mostrado, incluso si supera el límite solicitado. Los recomendadores de controladoras y SLAM también conservan los empates; ya evaluaban umbrales con cumplimiento binario y mantienen peso igual por requisito solicitado.

Los pesos son una política configurable de priorización, no una medida universal de desempeño ni un dictamen legal de admisibilidad. El ensayo de precisión conserva 6 puntos por componente en mm, el ppm 2, IP 5 y temperatura 4. Se reduce el predominio de funciones comerciales y se refuerzan interoperabilidad y capacidad obligatoria. Los pesos existentes personalizados y criterios desactivados en Admin se respetan; solo se actualizan los valores de fábrica anteriores.

| Criterio | Peso anterior de fábrica | Peso revisado |
|---|---:|---:|
| IMU | 10 | 4 |
| Cámara | 8 | 3 |
| Cantidad de cámaras | 6 | 3 |
| Láser | 8 | 4 |
| Canales GNSS | 5 | 3 |
| Memoria | 3 | 5 |
| USB-C | 2 | 4 |
| Radio UHF integrada Tx/Rx | 3 | 5 |
| GPS | 1 | 2 |
| GLONASS | 1 | 2 |
| Galileo | 1 | 2 |
| BeiDou | 1 | 2 |
| QZSS | 1 | 2 |

Una calificación alta no sustituye la revisión de los requisitos obligatorios. `aptitud` distingue incumplimiento conocido, verificación pendiente y cumplimiento de los criterios evaluados. Los requisitos no representados por los campos de Licitex siguen pendientes de revisión manual.

## Repetición de la licitación anterior

Se reutilizaron sus requisitos técnicos interpretados, sin otra llamada al proveedor de IA y sin consumir cuota de Gemini. Con el filtro solo COTECMI se obtuvieron los 13 receptores publicados; los cuatro primeros conservan el mismo puesto.

| Equipo | Puesto | Cumplimiento ponderado | Incumplimientos | Pendientes |
|---|---:|---:|---:|---:|
| Orion ONE | 1 | 97.17 % | 0 | 1 |
| X1 | 1 | 97.17 % | 0 | 1 |
| X1 Lite | 1 | 97.17 % | 0 | 1 |
| Z1 | 1 | 97.17 % | 0 | 1 |
| Jupiter Laser RTK | 5 | 95.28 % | 1 | 0 |
| Mars Pro Laser RTK | 6 | 93.40 % | 1 | 1 |
| T300+ | 6 | 93.40 % | 1 | 1 |
| T20 Palm RTK | 8 | 87.74 % | 2 | 2 |
| Reach RS3 | 9 | 69.81 % | 6 | 2 |
| Sfaira ONE Plus | 10 | 66.98 % | 4 | 5 |
| P6H Portátil | 11 | 60.38 % | 7 | 5 |
| Reach RS2 | 12 | 57.55 % | 9 | 2 |
| Reach RS2+ | 12 | 57.55 % | 9 | 2 |

Jupiter supera ahora a Mars Pro: 95,28 % frente a 93,40 %. Jupiter pierde el requisito de memoria interna mínima; Mars Pro pierde USB-C y tiene RINEX 3.x pendiente. Esto explica la diferencia en esta consulta concreta, sin declarar que un modelo sea siempre mejor para todas las licitaciones. Los SingularXYZ de primer puesto mantienen pendiente la norma de vibración, por lo que 97,17 % no equivale a cumplimiento total.

## Inventario de fuentes y pendientes

Los recuentos siguientes son de campos, no de equipos ni de incumplimientos. «Pendientes» incluye kit y modos sin desglose; «No aplica» significa una función ausente documentada o un campo dependiente de ella. Las variantes específicas y los nombres de PDF constan en el inventario JSON.

| Equipo | Categoría | Valores contrastados | Pendientes | No aplica | Fuente del fabricante |
|---|---|---:|---:|---:|---|
| SingularXYZ SC260 | Controladora | 1 | 7 | 0 | [Fuente](https://www.singularxyz.com/product_detail/SC260) |
| SinoGNSS R60 | Controladora | 1 | 2 | 0 | [Fuente](https://www.comnavtech.com/fr/product/handhold/R60.html) |
| SinoGNSS R80 | Controladora | 4 | 3 | 0 | [Fuente](https://www.comnavtech.com/fr/product/handhold/R80.html) |
| Gexcel HERON LITE | Escáner SLAM | 5 | 3 | 1 | [Fuente](https://heron.gexcel.it/en/gexcel-solutions-for-3d-surveying/heron-portable-3d-mapping-systems/heron-lite/) |
| SingularXYZ H1 | Escáner SLAM | 2 | 6 | 0 | [Fuente](https://www.singularxyz.com/product_detail/H1_Scanner) |
| SingularXYZ H2 | Escáner SLAM | 0 | 4 | 0 | [Fuente](https://singularxyz.com/product_detail/H2_Scanner) |
| SinoGNSS LS600 | Escáner SLAM | 4 | 7 | 0 | [Fuente](https://www.comnavtech.com/product/3d/LS600.html) |
| CHCNAV i50 | GNSS | 7 | 14 | 8 | [Fuente](https://chcnav.com/uploads/i50_DS_EN.pdf) |
| CHCNAV i73 | GNSS | 8 | 18 | 6 | [Fuente](https://geospatial.chcnav.com/) |
| CHCNAV i73+ | GNSS | 4 | 17 | 4 | [Fuente](https://chcnav.com/dam/jcr%3A00ee4b28-4f64-49a8-8eaa-14cdc03ff129/i73%2B_DS_EN.pdf) |
| CHCNAV i93 | GNSS | 3 | 13 | 1 | [Fuente](https://geospatial.chcnav.com/) |
| Emlid Reach RS2 | GNSS | 9 | 25 | 9 | [Fuente](https://docs.emlid.com/reachrs2/specifications/specs/) |
| Emlid Reach RS2+ | GNSS | 9 | 25 | 9 | [Fuente](https://emlid.com/reachrs2plus/) |
| Emlid Reach RS3 | GNSS | 9 | 26 | 6 | [Fuente](https://docs.emlid.com/reachrs3/specifications/specs/) |
| Leica GS16 | GNSS | 2 | 17 | 6 | [Fuente](https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-viva-gs16) |
| Leica GS18 T | GNSS | 2 | 16 | 3 | [Fuente](https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-gs18-t) |
| Leica GS18I | GNSS | 3 | 16 | 1 | [Fuente](https://leica-geosystems.com/products/gnss-systems/smart-antennas/leica-gs18-i) |
| Leica Viva GS10 | GNSS | 2 | 13 | 7 | [Fuente](https://leica-geosystems.com/-/media/files/leicageosystems/products/brochures/leica_viva_gs10_25_bro.ashx?la=en) |
| Leica Viva GS25 | GNSS | 2 | 13 | 7 | [Fuente](https://leica-geosystems.com/-/media/files/leicageosystems/products/brochures/leica_viva_gs10_25_bro.ashx?la=en) |
| SingularXYZ Orion ONE | GNSS | 5 | 20 | 1 | [Fuente](https://www.singularxyz.com/product_detail/Orion_ONE) |
| SingularXYZ Sfaira ONE Plus | GNSS | 14 | 31 | 5 | [Fuente](https://www.singularxyz.com/product_detail/Sfaira_ONE_Plus) |
| SingularXYZ X1 | GNSS | 6 | 17 | 3 | [Fuente](https://www.singularxyz.com/product_detail/X1) |
| SingularXYZ X1 Lite | GNSS | 6 | 17 | 3 | [Fuente](https://www.singularxyz.com/product_detail/X1_Lite) |
| SingularXYZ Z1 | GNSS | 8 | 18 | 4 | [Fuente](https://www.singularxyz.com/product_detail/Z1) |
| SinoGNSS Jupiter Laser RTK | GNSS | 13 | 14 | 1 | [Fuente](https://www.comnavtech.com/product/receiver/Jupiter.html) |
| SinoGNSS Mars Pro Laser RTK | GNSS | 10 | 14 | 2 | [Fuente](https://www.comnavtech.com/product/receiver/marpro.html) |
| SinoGNSS P6H Portátil | GNSS | 3 | 33 | 5 | [Fuente](https://www.comnavtech.com/) |
| SinoGNSS T20 Palm RTK | GNSS | 6 | 13 | 6 | [Fuente](https://comnavtech.com/product/receiver/t20.html) |
| SinoGNSS T300+ | GNSS | 7 | 13 | 5 | [Fuente](https://www.comnavtech.com/product/receiver/t300plus.html) |
| South Galaxy G1 | GNSS | 5 | 14 | 5 | [Fuente](https://www.southinstrument.com/company/details/id/77.html) |
| South Galaxy G6 | GNSS | 3 | 23 | 3 | [Fuente](https://www.southinstrument.com/company/details/id/77.html) |
| Trimble R12i | GNSS | 4 | 12 | 3 | [Fuente](https://help.fieldsystems.trimble.com/trimble-access/latest/en/equipment-supported.htm) |
| Trimble R8s | GNSS | 7 | 12 | 8 | [Fuente](https://help.fieldsystems.trimble.com/trimble-access/latest/en/equipment-supported.htm) |

## Validación y aplicación

- 75 pruebas unitarias aprobadas, incluidas memoria interna/tarjeta, mínimos estrictos, ausencia de sensores, evidencia y empates.
- Compilación de producción del frontend y comprobación de TypeScript aprobadas.
- Consulta HTTP de las 33 fichas y todas las columnas técnicas de sus comparadores aprobada, sin valores nulos visuales. Los 618 campos nulos técnicos tienen evidencia y clasificación. Puede repetirse con `scripts/verificar_auditoria_20261020.py` (solo lectura).
- Empate conservado con límite 1: tres controladoras y cuatro SLAM en los casos verificados.
- Migración 25 aplicada transaccionalmente en la base configurada y registrada; se incorpora al mecanismo de migración de producción.

La generación de SQL puede reproducirse con `scripts/preparar_auditoria_20261020.py --snapshot RUTA_JSON`. Requiere un inventario previo con las claves `equipos`, `gnss`, `controladoras` y `slam`, sin secretos. El inventario de datos previo se conserva localmente en la carpeta ignorada `tmp/catalog-audit/`; no se publica una copia completa de la base. La migración SQL y el inventario de cambios sí quedan versionados.
