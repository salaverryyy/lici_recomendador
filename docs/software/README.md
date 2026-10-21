# Software de oficina y propuestas completas

Auditoría: 21 de octubre de 2026. El inventario trazable está en [catalogo_2026-10-21.json](catalogo_2026-10-21.json), con fuentes oficiales, fecha, alcance y funciones no confirmadas. No se importa ningún ejecutable de terceros ni se afirma una versión reciente que no esté comprobada.

| Programa | Ecosistema | Evidencia principal |
|---|---|---|
| PProcessing | SingularXYZ | [Ficha del fabricante](https://www.singularxyz.com/product_detail/PProcessing): estático/cinemático, ajuste de redes, RINEX 2.x/3.x, salidas DXF/TXT/KML/CSV e informes HTML. |
| Compass Solution | SinoGNSS / ComNav | [Producto oficial](https://www.comnavtech.com/sp/product/software/Compass%20Solution.html): estático/rápido/cinemático e informes. [Ficha N3](https://www.comnavtech.com/uploads/soft/20250606/4cf6ea262b3d28e11c75a61c53fc2eb6.pdf): observaciones RINEX y binarias. |
| Emlid Studio | Emlid | [Producto](https://emlid.com/emlid-studio/) y [manual](https://docs.emlid.com/emlid-studio/): gratuito, Windows/macOS, estático, cinemático, drones, Stop & Go y conversión RINEX. |

La auditoría incremental documentada en [auditoria_2026-10-21.md](auditoria_2026-10-21.md) confirma Windows para PProcessing/Compass y ajuste de redes por mínimos cuadrados para Compass. No se asignan gratuidad, licencia incluida o modalidad perpetua sin evidencia. En Emlid Studio tampoco se presume ajuste de redes ni exportaciones no documentadas. Software gratuito no acredita una licencia comercial exigida. Estos programas son de oficina; no se presentan como aplicaciones Android de la colectora. Survey Master, SingularPad y Emlid Flow tienen un papel diferente.

## Catálogo y datos

- `/software`: catálogo público, buscador, funciones, formatos, condiciones y fuentes.
- `GET /api/software`: solo Cotecmi por defecto; filtro ampliable por API. Los tres programas pertenecen a marcas del catálogo Cotecmi existente, sin crear nuevas marcas comerciales.
- Tabla `software_procesamiento`, separada del hardware; visible en Admin → Tablas. La edición específica del software no forma parte de esta entrega.
- Migración `26_software_procesamiento`: inserción inicial sin sobrescribir futuras correcciones administrativas. Registrada para producción en el mecanismo existente.
- Regeneración del SQL: `scripts/preparar_software.py` desde el inventario auditado. Sin claves ni credenciales en los archivos.

## Conversación y recomendaciones

La IA extrae requisitos separados de GNSS, controladora y software. Puede responder una consulta conjunta (`kit`) o mantener requisitos por familia entre turnos. El tipo elegido en la interfaz orienta la consulta sin borrar el contexto; el mensaje actual puede cambiar de familia. Las selecciones del usuario son IDs validados contra el catálogo publicado y el filtro Cotecmi vigente. Una referencia provisional es distinta de una elección confirmada: el botón «Elegir este GNSS para continuar» fija el receptor sin consumir una consulta adicional.

El receptor seleccionado se conserva al continuar con colectora/software; los otros bloques se recalculan al cambiar los requisitos. Las opciones se presentan en orden GNSS → controladora → software. Cada receptor se asocia por defecto al software auditado de su marca; esta relación comercial no suma puntos ni acredita compatibilidad del conjunto. Si no hay programa de esa marca, se informa la ausencia sin sustituirlo por uno de otra marca automáticamente.

Si se exige misma marca para TODO el conjunto, se excluyen controladoras de otras marcas. La exigencia de igual marca para base/rovers no se convierte en una restricción global sin petición expresa. El catálogo actual no incluye una controladora Emlid: se señala esta ausencia cuando se exige igualdad global; en otros casos, una candidata de otra marca requiere validar app/enlace. No se presume que Bluetooth o Android basten para comunicar dos equipos.

La evaluación conjunta considera las tres familias con requisitos: media de sus porcentajes, con igual peso por familia evaluada. La falta de requisitos en una familia no concede un 100 % ficticio. Los mínimos incumplidos del software dan cero puntos y los no publicados quedan pendientes. Los conjuntos con incumplimientos conocidos se presentan después de las propuestas sin incumplimientos conocidos; no se declara ningún conjunto plenamente conforme solo por su puntaje. Se mantienen los empates en el límite solicitado. Para cada GNSS se muestra una controladora candidata y otras alternativas de catálogo, sin afirmar que estén técnicamente empatadas.

La verificación final conserva cantidades, accesorios, licencias, versiones, formatos concretos, kit y requisitos no representados como pendientes. Requiere comprobar registro bruto del receptor, archivo de prueba y app de campo. Si el usuario cambia el receptor y mantiene un software incompatible por marca con la selección, se informa que no hay una combinación auditada; no se ignora silenciosamente su selección.

El historial se guarda localmente en el navegador, sin límite automático de cinco chats ni recorte de mensajes visibles. La lista es desplazable y la eliminación manual. No se crean almacenamiento externo ni servicios de pago. Solo los últimos seis turnos, acotados en longitud, se envían al modelo; guardar más chats no amplía ese contexto ni añade llamadas. Si el navegador rechaza el guardado por falta de espacio o bloqueo, se avisa y se conservan los cambios en la sesión, sin borrar chats automáticamente. Borrar los datos del sitio elimina el historial local y no hay sincronización entre dispositivos.

## Espera y accesibilidad

La respuesta pendiente muestra tres puntos animados, segundos de espera y mensajes informativos rotativos cada siete segundos. Son explicaciones sobre la evaluación, no telemetría de etapas internas de Gemini. No se muestran porcentajes ficticios, pensamiento privado ni tareas supuestamente terminadas. La animación respeta `prefers-reduced-motion`; temporizadores se limpian al finalizar/desmontar.

## Verificación

86 pruebas unitarias aprobadas, incluidas componentes, mínimos, datos desconocidos, selección y alcance Cotecmi; compilación TypeScript/producción aprobada. `scripts/verificar_software.py` comprueba por HTTP el catálogo y una secuencia de tres turnos y una consulta conjunta con BD real e IA simulada, sin consumir cuota. No modifica registros. También se verificó una consulta real con Gemini: extrajo las tres familias y devolvió X1 + controladora + PProcessing; no se cambiaron modelo, claves ni plan de facturación.
