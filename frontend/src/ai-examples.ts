import { readStored, writeStored } from "./persist";

export const EXAMPLES = [
  "Necesito un GNSS para replanteo urbano con IMU y autonomía para toda la jornada.",
  "Compara receptores con USB-C y aclara cuáles necesitan un adaptador.",
  "Busco una base y dos rovers de la misma marca, con radio UHF integrada.",
  "¿Qué GNSS ofrece 8 GB internos, aunque tenga que pedir esa configuración de fábrica?",
  "Necesito medir puntos inaccesibles con láser. Compara alcance y precisión.",
  "Quiero un GNSS con ranura SIM y módem 4G propios, sin depender del teléfono.",
  "¿Qué opciones económicas cumplen RTK horizontal de 8 mm + 1 ppm e IMU de 60°?",
  "Compara Jupiter y Mars Pro para una obra con obstáculos y jornadas largas.",
  "Estoy entre X1 y Orion ONE. Si ambos cumplen mi trabajo, ¿cuál conviene por costo?",
  "Necesito registrar observaciones para posproceso estático y exportar RINEX.",
  "Busco una controladora con Android, teclado físico y al menos 4 GB de RAM.",
  "Compara R60 y R80 para trabajar bajo lluvia y con guantes.",
  "Ya elegí un receptor SinoGNSS. ¿Qué controladora y software de oficina lo acompañan?",
  "Necesito una colectora con SIM, LTE y pantalla legible al sol.",
  "¿Qué diferencia hay entre una controladora dedicada y usar Emlid Flow en mi teléfono?",
  "Busco un escáner SLAM para una mina, con 70 m de alcance y 200 000 puntos/s.",
  "Necesito levantar interiores sin señal GNSS y obtener una nube de puntos coloreada.",
  "Compara LS600, H1 y H2 para documentar una edificación.",
  "Para un túnel, ¿qué SLAM recomendarías y qué limitaciones tendría que revisar?",
  "Busco un SLAM ligero, con dos horas de autonomía y exportación LAS o E57.",
  "Necesito escanear patrimonio y fachadas. Prioriza detalle, color y portabilidad.",
  "¿Qué software de oficina permite ajuste de redes e importar RINEX 2 y 3?",
  "Compara Compass Solution y PProcessing para líneas base y ajuste de redes.",
  "Quiero procesar datos PPK de un dron. ¿Qué software y archivos necesito?",
  "¿Cuándo me conviene Emlid Studio y qué tendría que confirmar para una licitación?",
  "Necesito una solución completa: receptor, controladora y software de procesamiento.",
  "Te pasaré una licitación escaneada. Separa los requisitos legibles de los dudosos.",
  "¿Qué alternativas cumplen mi licitación con memoria ampliada o accesorios incluidos?",
  "Prioriza Cotecmi y explícame los requisitos que ningún equipo pueda acreditar.",
  "Tengo varias opciones empatadas. Compara costo orientativo, año y condiciones pendientes.",
];

export function nextExamples(count = 3): string[] {
  const key = "licitex-ia-ejemplos-v1";
  const recentKey = key + "-recientes";
  const recentStored = readStored<unknown>(recentKey, []);
  const recent = Array.isArray(recentStored) ? recentStored.slice(-6) : [];
  const queueStored = readStored<unknown>(key, []);
  let queue = Array.from(
    new Set(
      (Array.isArray(queueStored) ? queueStored : []).filter(
        (i) => Number.isInteger(i) && i >= 0 && i < EXAMPLES.length,
      ),
    ),
  ) as number[];
  const selected: number[] = [];
  while (selected.length < count) {
    if (!queue.length) {
      queue = Array.from(EXAMPLES.keys()).filter(
        (i) => !selected.includes(i) && !recent.includes(i),
      );
      for (let i = queue.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [queue[i], queue[j]] = [queue[j], queue[i]];
      }
    }
    const index = queue.shift()!;
    if (!selected.includes(index)) selected.push(index);
  }
  writeStored(key, queue);
  writeStored(recentKey, [...recent, ...selected].slice(-6));
  return selected.map((i) => EXAMPLES[i]);
}
