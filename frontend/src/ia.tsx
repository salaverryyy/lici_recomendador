import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Bot, MessageSquareText, Plus, Send, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "./api";
import { usePersistentState } from "./persist";
import { SoftwareCard } from "./software";

type Context = {
  tipo_equipo: "gnss" | "controladora" | "slam" | "software" | "kit";
  requisitos: Record<string, unknown>;
  componentes?: Record<string, Record<string, unknown>>;
  selecciones?: Record<string, string>;
  referencia_gnss?: string;
  misma_marca?: boolean;
};
type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  data?: any;
};
type Chat = {
  id: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  type: "auto" | "gnss" | "controladora" | "slam" | "software" | "kit";
  onlyCotecmi: boolean;
  context?: Context;
  messages: Message[];
};

// v2 inicia las búsquedas en el catálogo Cotecmi; el usuario puede ampliar cada chat.
const STORAGE_KEY = "licitex-ia-chats-v2";
const ACTIVE_KEY = "licitex-ia-chat-activo-v2";
const id = () => crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`;
const makeChat = (): Chat => {
  const now = Date.now();
  return {
    id: id(),
    title: "Nueva consulta",
    createdAt: now,
    updatedAt: now,
    type: "auto",
    onlyCotecmi: true,
    messages: [],
  };
};
const titleFor = (text: string) =>
  text.trim().replace(/\s+/g, " ").slice(0, 48) || "Nueva consulta";
const fieldLabel = (key: string) =>
  key.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
const display = (value: unknown) =>
  typeof value === "boolean" ? (value ? "Sí" : "No") : String(value);

function BoldText({ text }: { text: unknown }) {
  return String(text ?? "")
    .split(/(\*\*[^*\n]+\*\*)/g)
    .filter(Boolean)
    .map((part, index) =>
      part.startsWith("**") && part.endsWith("**") ? (
        <strong key={`${index}-${part}`}>{part.slice(2, -2)}</strong>
      ) : (
        <span key={`${index}-${part}`}>{part}</span>
      ),
    );
}

function historyFor(messages: Message[]) {
  let remaining = 12_000;
  const selected: Array<Pick<Message, "role" | "text">> = [];
  for (const item of messages.slice(-12).reverse()) {
    if (remaining <= 0) break;
    const text = item.text.slice(0, Math.min(2500, remaining)).trim();
    if (!text) continue;
    selected.push({ role: item.role, text });
    remaining -= text.length;
  }
  return selected.reverse();
}

function cleanChats(value: unknown): Chat[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter(
      (chat) =>
        chat && typeof chat.id === "string" && Array.isArray(chat.messages),
    )
    .sort((a, b) => Number(b.updatedAt) - Number(a.updatedAt))
    .slice(0, 5) as Chat[];
}

function RankCard({ result, kind }: { result: any; kind: string }) {
  const failed = result.detalle?.filter((item: any) =>
    ["incumple", "no_cumple"].includes(item.estado),
  );
  const unknown = result.detalle?.filter(
    (item: any) => item.estado === "sin_datos",
  );
  return (
    <article className="ai-rank-card">
      <div className="rank-heading">
        <span className="rank-number">
          {result.posicion ? `#${result.posicion}` : "Opción"}
        </span>
        <Link to={`/equipos/${result.equipo.id_equipo}`}>
          <h3>
            {result.equipo.marca} {result.equipo.modelo}
          </h3>
        </Link>
        <strong>
          {result.porcentaje != null
            ? `${result.porcentaje}%`
            : "Sin requisitos para puntuar"}
        </strong>
      </div>
      {result.porcentaje != null && (
        <progress max={100} value={result.porcentaje} />
      )}
      <p className="small-text">
        {result.cumplimientos ?? 0} cumple · {failed?.length || 0} no cumple ·{" "}
        {unknown?.length || 0} sin datos
      </p>
      <p className="muted small-text">
        {result.porcentaje == null
          ? "Referencia sin evaluación técnica de requisitos."
          : "Cumplimiento verificado de los criterios evaluados."}
        {result.porcentaje_afinidad != null &&
        result.porcentaje_afinidad !== result.porcentaje
          ? ` Afinidad técnica: ${result.porcentaje_afinidad}% (incluye cercanía a umbrales incumplidos; no acredita cumplimiento).`
          : ""}
      </p>
      <details className="score-details">
        <summary>Ver evaluación</summary>
        <dl>
          {result.detalle?.map((item: any) => (
            <div key={item.clave}>
              <dt>{item.nombre}</dt>
              <dd>
                <span className={`ai-state ${item.estado}`}>
                  {item.estado === "cumple"
                    ? "Cumple"
                    : item.estado === "sin_datos"
                      ? "Sin datos"
                      : "No cumple"}
                </span>
                {kind === "controladora" && item.valor != null
                  ? ` · ${display(item.valor)} ${item.unidad || ""}`
                  : ""}
              </dd>
            </div>
          ))}
        </dl>
      </details>
    </article>
  );
}

function AssistantAnswer({
  data,
  onSelect,
}: {
  data: any;
  onSelect?: (id: string) => void;
}) {
  if (data?.estado === "no_disponible") {
    return (
      <div className="notice error">
        {data.codigo && <strong>Error {data.codigo}: </strong>}
        {data.mensaje}
        {data.reintentar_en && (
          <>
            {" "}
            Puedes volver a intentarlo desde{" "}
            {new Date(data.reintentar_en).toLocaleString("es-PE")}.
          </>
        )}
      </div>
    );
  }
  const results = data?.ranking?.resultados || [];
  return (
    <>
      <p>
        <BoldText text={data?.respuesta} />
      </p>
      {data?.resumen && (
        <p className="muted">
          <strong>Interpretación:</strong> <BoldText text={data.resumen} />
        </p>
      )}
      {data?.requisitos && (
        <div className="ai-requirements">
          {Object.entries(data.requisitos).map(([key, value]) => (
            <span key={key}>
              {fieldLabel(key)}: {display(value)}
            </span>
          ))}
        </div>
      )}
      {!!data?.preguntas?.length && (
        <div className="notice">
          <strong>Para afinar el resultado:</strong>
          <ul>
            {data.preguntas.map((question: string) => (
              <li key={question}>
                <BoldText text={question} />
              </li>
            ))}
          </ul>
        </div>
      )}
      {!!data?.omitidos?.length && (
        <div className="notice">
          <strong>Evaluación parcial: quedan requisitos por verificar.</strong>
          <p>
            El porcentaje no acredita el cumplimiento total de la licitación.
          </p>
          <ul>
            {data.omitidos.map((item: string, index: number) => (
              <li key={`${index}-${item}`}>
                <BoldText text={item} />
              </li>
            ))}
          </ul>
        </div>
      )}
      {!!data?.solucion?.opciones?.length && (
        <section className="ai-ranking">
          <h3>Propuestas del conjunto</h3>
          <p className="muted small-text">{data.solucion.nota}</p>
          {data.solucion.opciones.map((option: any, index: number) => (
            <details
              className="panel solution-option"
              key={option.gnss.equipo.id_equipo}
              open={index === 0}
            >
              <summary>
                {option.gnss.equipo.marca} {option.gnss.equipo.modelo} →{" "}
                {option.controladora?.equipo.modelo ||
                  option.app_campo?.nombre ||
                  "Controladora pendiente"}{" "}
                → {option.software?.software.nombre || "Software pendiente"} ·{" "}
                {option.estado === "no_cumple"
                  ? "Tiene incumplimientos"
                  : "Requiere validación"}
              </summary>
              {option.porcentaje != null && (
                <p>
                  <strong>{option.porcentaje}%</strong> de cumplimiento parcial
                  del conjunto. {option.incumplimientos} incumplimientos ·{" "}
                  {option.sin_datos} datos pendientes.
                </p>
              )}
              {!!option.familias_sin_requisitos.length && (
                <p className="notice">
                  Sin requisitos técnicos para puntuar:{" "}
                  {option.familias_sin_requisitos.join(", ")}.
                </p>
              )}
              <h4>1. Receptor GNSS</h4>
              <RankCard result={option.gnss} kind="gnss" />
              {onSelect && (
                <button
                  type="button"
                  className="outline"
                  onClick={() => onSelect(option.gnss.equipo.id_equipo)}
                >
                  Elegir este GNSS para continuar
                </button>
              )}
              <h4>2. Controladora</h4>
              {option.controladora ? (
                <RankCard result={option.controladora} kind="controladora" />
              ) : option.app_campo ? (
                <p>
                  <a
                    href={option.app_campo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {option.app_campo.nombre}
                  </a>
                  . {option.app_campo.nota}
                </p>
              ) : (
                <p>No se encontró una controladora que respete la selección.</p>
              )}
              {!!option.alternativas_controladora?.length && (
                <p className="small-text">
                  Otras controladoras a revisar:{" "}
                  {option.alternativas_controladora
                    .map((e: any) => `${e.marca} ${e.modelo}`)
                    .join(", ")}
                  .
                </p>
              )}
              <h4>3. Software de procesamiento de oficina</h4>
              {option.software ? (
                <SoftwareCard
                  software={option.software.software}
                  evaluation={option.software}
                />
              ) : (
                <p>No hay software de esta marca auditado para la selección.</p>
              )}
              <ul className="small-text">
                {option.pendientes.map((p: string) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </details>
          ))}
        </section>
      )}
      {data.tipo_equipo === "software" &&
        !data?.solucion?.opciones?.length &&
        data?.rankings?.software?.resultados?.map((r: any) => (
          <SoftwareCard
            key={r.software.id_software}
            software={r.software}
            evaluation={r}
          />
        ))}
      {results.length > 0 && !data?.solucion?.opciones?.length && (
        <div className="ai-ranking">
          <h3>Equipos recomendados</h3>
          <p className="muted small-text">
            Se muestran hasta 20 equipos, incluyendo todos los empatados en el
            último puesto. Las funciones no solicitadas no suman puntos.
          </p>
          {results.map((result: any) => (
            <div key={result.equipo.id_equipo}>
              <RankCard result={result} kind={data.tipo_equipo} />
              {data.tipo_equipo === "gnss" && onSelect && (
                <button
                  type="button"
                  className="outline"
                  onClick={() => onSelect(result.equipo.id_equipo)}
                >
                  Elegir este GNSS para continuar
                </button>
              )}
            </div>
          ))}
        </div>
      )}
      {data?.uso && (
        <p className="muted ai-usage">
          {data.uso.proveedor} · {data.uso.modelo}
          {data.uso.tokens_entrada
            ? ` · ${data.uso.tokens_entrada + (data.uso.tokens_salida || 0)} tokens`
            : ""}
        </p>
      )}
      {data?.memoria?.mensajes_usados > 0 && (
        <p className="muted ai-usage">
          Memoria activa · {data.memoria.mensajes_usados} mensajes anteriores ·{" "}
          {data.memoria.equipos_recuperados?.length || 0} fichas técnicas
          recuperadas
        </p>
      )}
    </>
  );
}

function WaitingResponse({ query, type }: { query: string; type: string }) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    const start = Date.now();
    const timer = setInterval(
      () => setSeconds(Math.floor((Date.now() - start) / 1000)),
      1000,
    );
    return () => clearInterval(timer);
  }, []);
  const software = /software|p\s?processing|compass|emlid studio|rinex/i.test(
    query,
  );
  const hardware =
    /receptor|jupiter|mars|\bx1\b|t300/i.test(query) ||
    (!software && /\bgnss\b|\brover|\bbase\b/i.test(query));
  const controller = /controladora|colectora|\br80\b|sc260/i.test(query);
  const slam = /\bslam\b|lidar|esc[aá]ner|ls600|heron|\bh[12]\b/i.test(query);
  const scope =
    Number(software) + Number(controller) + Number(slam) + Number(hardware) > 1
      ? "kit"
      : software
        ? "software"
        : controller
          ? "controladora"
          : slam
            ? "slam"
            : hardware
              ? "gnss"
              : type;
  const specific: Record<string, string[]> = {
    software: [
      "La consulta se centra en software de procesamiento.",
      "Los formatos RINEX, las funciones y las licencias condicionan la elección.",
      "Una función pendiente de confirmar no equivale a una función ausente.",
    ],
    gnss: [
      "La consulta se centra en receptores GNSS.",
      "La precisión, las señales y la conectividad se contrastan con el catálogo.",
    ],
    controladora: [
      "La consulta se centra en controladoras.",
      "El sistema operativo, la memoria y la autonomía condicionan la elección.",
    ],
    slam: [
      "La consulta se centra en escáneres SLAM.",
      "El alcance LiDAR, la precisión y la aplicación condicionan la elección.",
    ],
    kit: [
      "La consulta abarca varios componentes de la solución.",
      "La compatibilidad del conjunto y sus licencias requieren verificación.",
    ],
  };
  const messages = [
    "Tu consulta está en proceso.",
    ...(specific[scope] || [
      "La respuesta utilizará los datos técnicos disponibles.",
    ]),
    "Los datos sin confirmar se mostrarán como pendientes.",
  ];
  return (
    <div className="ai-message assistant" role="status">
      <div className="ai-message-label">Lici</div>
      <p>
        Preparando la respuesta
        <span className="thinking-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
      </p>
      <p className="muted small-text">
        {messages[Math.floor(seconds / 7) % messages.length]}
      </p>
      <small className="muted">
        {seconds} s de espera · El tiempo depende del proveedor de IA.
      </small>
    </div>
  );
}

export function AiAdvisor() {
  const [storedChats, setChats] = usePersistentState<Chat[]>(STORAGE_KEY, [
    makeChat(),
  ]);
  const chats = useMemo(() => cleanChats(storedChats), [storedChats]);
  const [activeId, setActiveId] = usePersistentState<string>(ACTIVE_KEY, "");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [availability, setAvailability] = useState<any>(null);
  const initializedEmptyHistory = useRef(false);
  const active = chats.find((chat) => chat.id === activeId) || chats[0];

  useEffect(() => {
    if (!chats.length && !initializedEmptyHistory.current) {
      initializedEmptyHistory.current = true;
      const chat = makeChat();
      setChats([chat]);
      setActiveId(chat.id);
    } else if (chats[0] && !chats.some((chat) => chat.id === activeId)) {
      setActiveId(chats[0].id);
    }
  }, [activeId, chats, setActiveId]);
  useEffect(() => {
    let active = true;
    const check = () =>
      api("/ia/estado?comprobar=true")
        .then((value) => active && setAvailability(value))
        .catch(
          (e) =>
            active &&
            setAvailability({ disponible: false, mensaje: e.message }),
        );
    check();
    const interval = window.setInterval(check, 60_000);
    window.addEventListener("focus", check);
    return () => {
      active = false;
      window.clearInterval(interval);
      window.removeEventListener("focus", check);
    };
  }, []);

  function createChat() {
    const chat = makeChat();
    setChats((previous) => [chat, ...cleanChats(previous)].slice(0, 5));
    setActiveId(chat.id);
    setMessage("");
    setError("");
    return chat;
  }

  function updateChat(chat: Chat) {
    setChats((previous) =>
      [
        chat,
        ...cleanChats(previous).filter((item) => item.id !== chat.id),
      ].slice(0, 5),
    );
  }

  function patchActive(changes: Partial<Chat>) {
    if (!active) return;
    updateChat({ ...active, ...changes, updatedAt: Date.now() });
  }

  function removeChat(chatId: string) {
    const remaining = chats.filter((chat) => chat.id !== chatId);
    if (!remaining.length) {
      const replacement = makeChat();
      setChats([replacement]);
      setActiveId(replacement.id);
    } else {
      setChats(remaining);
      if (activeId === chatId) setActiveId(remaining[0].id);
    }
  }

  async function send(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || busy) return;
    const current = active || createChat();
    const userMessage: Message = { id: id(), role: "user", text };
    const pending: Chat = {
      ...current,
      title: current.messages.length ? current.title : titleFor(text),
      updatedAt: Date.now(),
      messages: [...current.messages, userMessage],
    };
    updateChat(pending);
    setMessage("");
    setBusy(true);
    setError("");
    try {
      const data = await api("/ia/recomendar", "POST", {
        mensaje: text,
        tipo_equipo: pending.type,
        solo_cotecmi: pending.onlyCotecmi,
        top_n: 20,
        contexto_previo: pending.context || undefined,
        historial: historyFor(current.messages),
      });
      const assistant: Message = {
        id: id(),
        role: "assistant",
        text: data.respuesta || data.mensaje,
        data,
      };
      const completed: Chat = {
        ...pending,
        updatedAt: Date.now(),
        context:
          data.estado === "ok"
            ? data.contexto || {
                tipo_equipo: data.tipo_equipo,
                requisitos: data.requisitos,
              }
            : pending.context,
        // Diez turnos por consulta mantienen el historial útil sin agotar
        // el almacenamiento local con respuestas técnicas extensas.
        messages: [...pending.messages, assistant].slice(-20),
      };
      updateChat(completed);
      if (data.estado === "ok") setAvailability({ disponible: true });
      else if (
        !["respuesta_invalida", "respuesta_truncada"].includes(data.motivo)
      )
        setAvailability({ disponible: false, ...data });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const retry = availability?.reintentar_en
    ? new Date(availability.reintentar_en).toLocaleString("es-PE")
    : null;

  return (
    <main className="container ai-page">
      <div className="page-title">
        <div>
          <span className="eyebrow">CONVERSA CON LICI</span>
          <h1>Asistente para elegir equipos</h1>
          <p className="muted">
            Describe tu necesidad en lenguaje natural. Lici interpreta los
            requisitos y usa el ranking verificable de Licitex.
          </p>
        </div>
        <span
          className={`ai-availability ${availability?.disponible ? "online" : "offline"}`}
        >
          IA limitada · Capa gratuita ·{" "}
          {availability?.disponible ? "Disponible ahora" : "No disponible"}
        </span>
      </div>

      {!availability?.disponible && availability && (
        <div className="notice error">
          {availability.codigo && (
            <strong>Error {availability.codigo}: </strong>
          )}
          {availability.mensaje}
          {retry ? ` Puedes volver a intentarlo desde ${retry}.` : ""}
        </div>
      )}

      <div className="ai-shell">
        <aside className="ai-history panel">
          <button type="button" className="full" onClick={createChat}>
            <Plus size={16} /> Nueva consulta
          </button>
          <p className="muted small-text">
            Se guardan automáticamente las últimas 5 consultas en este
            navegador. Lici recuerda el contexto dentro de cada consulta.
          </p>
          <div className="ai-chat-list">
            {chats.map((chat) => (
              <div
                className={chat.id === active?.id ? "active" : ""}
                key={chat.id}
              >
                <button
                  type="button"
                  className="ai-chat-select"
                  onClick={() => setActiveId(chat.id)}
                >
                  <MessageSquareText size={15} />
                  <span>{chat.title}</span>
                </button>
                <button
                  type="button"
                  className="icon"
                  aria-label={`Eliminar ${chat.title}`}
                  onClick={() => removeChat(chat.id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
            {!chats.length && (
              <p className="muted small-text">
                Todavía no hay consultas guardadas.
              </p>
            )}
          </div>
        </aside>

        <section className="ai-conversation panel">
          <div className="ai-controls">
            <label>
              Tipo de equipo
              <select
                value={active?.type || "auto"}
                disabled={!active || busy}
                onChange={(e) =>
                  patchActive({
                    type: e.target.value as Chat["type"],
                  })
                }
              >
                <option value="auto">Detectar automáticamente</option>
                <option value="gnss">Receptor GNSS</option>
                <option value="controladora">Controladora</option>
                <option value="slam">Escáner SLAM</option>
                <option value="software">Software de procesamiento</option>
                <option value="kit">
                  Conjunto GNSS + controladora + software
                </option>
              </select>
            </label>
            <label>
              Equipos a evaluar
              <select
                value={String(active?.onlyCotecmi ?? false)}
                disabled={!active || busy}
                onChange={(e) =>
                  patchActive({ onlyCotecmi: e.target.value === "true" })
                }
              >
                <option value="true">Solo Cotecmi</option>
                <option value="false">Cotecmi y competencia</option>
              </select>
            </label>
          </div>

          {active?.context?.selecciones?.gnss && (
            <p className="notice">
              GNSS elegido para continuar esta consulta.{" "}
              <Link to={`/equipos/${active.context.selecciones.gnss}`}>
                Ver ficha
              </Link>
            </p>
          )}

          <div className="ai-messages" aria-live="polite">
            {!active?.messages.length && (
              <div className="ai-welcome">
                <Bot size={38} />
                <h2>¿Qué equipo necesitas?</h2>
                <p>
                  Por ejemplo: “Busco un escáner SLAM para una mina, con 70 m de
                  alcance, colorización y al menos 200 000 puntos/s”.
                </p>
              </div>
            )}
            {active?.messages.map((item) => (
              <article className={`ai-message ${item.role}`} key={item.id}>
                <div className="ai-message-label">
                  {item.role === "user" ? "Tú" : "Lici"}
                </div>
                {item.role === "assistant" ? (
                  <AssistantAnswer
                    data={item.data}
                    onSelect={
                      busy
                        ? undefined
                        : (ident) =>
                            patchActive({
                              context: {
                                ...(active.context || item.data.contexto),
                                selecciones: {
                                  ...(active.context?.selecciones || {}),
                                  gnss: ident,
                                },
                                referencia_gnss: ident,
                              },
                            })
                    }
                  />
                ) : (
                  <p>
                    <BoldText text={item.text} />
                  </p>
                )}
              </article>
            ))}
            {busy && (
              <WaitingResponse
                query={
                  active?.messages.filter((m) => m.role === "user").at(-1)
                    ?.text || ""
                }
                type={active?.type || ""}
              />
            )}
          </div>

          {error && (
            <div role="alert" className="notice error">
              {error}
            </div>
          )}
          <form className="ai-composer" onSubmit={send}>
            <textarea
              value={message}
              maxLength={6000}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Describe el trabajo, las condiciones y las especificaciones que necesitas…"
              aria-label="Consulta para Lici"
            />
            <button
              disabled={busy || !message.trim() || !availability?.disponible}
            >
              <Send size={16} /> Enviar
            </button>
          </form>
          <p className="muted small-text">
            La IA interpreta el texto; la puntuación se calcula con los datos
            técnicos recuperados de Licitex. La memoria del chat permanece en
            este navegador y sólo se envían los últimos seis turnos al
            responder. Confirma ficha, accesorios y condiciones de la oferta. No
            ingreses información confidencial mientras uses el nivel gratuito.
          </p>
          <details className="ai-error-legend">
            <summary>Qué significan los códigos de error de la IA</summary>
            <dl>
              <div>
                <dt>400</dt>
                <dd>
                  La consulta no tuvo un formato aceptado por el proveedor.
                </dd>
              </div>
              <div>
                <dt>401 / 403</dt>
                <dd>
                  La clave no es válida o no tiene permiso para usar el modelo.
                </dd>
              </div>
              <div>
                <dt>404</dt>
                <dd>
                  El modelo configurado no existe o dejó de estar disponible.
                </dd>
              </div>
              <div>
                <dt>429</dt>
                <dd>
                  Se alcanzó la cuota gratuita o el límite temporal de
                  consultas.
                </dd>
              </div>
              <div>
                <dt>500</dt>
                <dd>El proveedor tuvo un error interno.</dd>
              </div>
              <div>
                <dt>502 · respuesta inválida o incompleta</dt>
                <dd>
                  La IA no entregó una respuesta completa y válida. Puedes
                  reenviar la consulta; esto no indica que se agotó la cuota.
                </dd>
              </div>
              <div>
                <dt>502 / 503 / 504</dt>
                <dd>
                  Falla temporal, saturación o demora del proveedor; Licitex
                  reintenta automáticamente.
                </dd>
              </div>
            </dl>
          </details>
        </section>
      </div>
    </main>
  );
}
