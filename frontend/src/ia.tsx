import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Bot, MessageSquareText, Plus, Send, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "./api";
import { usePersistentState } from "./persist";

type Context = {
  tipo_equipo: "gnss" | "controladora";
  requisitos: Record<string, unknown>;
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
  type: "auto" | "gnss" | "controladora";
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
        <span className="rank-number">#{result.posicion}</span>
        <Link to={`/equipos/${result.equipo.id_equipo}`}>
          <h3>
            {result.equipo.marca} {result.equipo.modelo}
          </h3>
        </Link>
        <strong>{result.porcentaje ?? "—"}%</strong>
      </div>
      {result.porcentaje != null && (
        <progress max={100} value={result.porcentaje} />
      )}
      <p className="small-text">
        {result.cumplimientos} cumple · {failed?.length || 0} no cumple ·{" "}
        {unknown?.length || 0} sin datos
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

function AssistantAnswer({ data }: { data: any }) {
  if (data?.estado === "no_disponible") {
    return (
      <div className="notice error">
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
      <p>{data?.respuesta}</p>
      {data?.resumen && (
        <p className="muted">
          <strong>Interpretación:</strong> {data.resumen}
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
              <li key={question}>{question}</li>
            ))}
          </ul>
        </div>
      )}
      {!!data?.omitidos?.length && (
        <p className="muted small-text">
          Revisión manual pendiente: {data.omitidos.join(", ")}.
        </p>
      )}
      {results.length > 0 && (
        <div className="ai-ranking">
          <h3>Equipos recomendados</h3>
          {results.map((result: any) => (
            <RankCard
              key={result.equipo.id_equipo}
              result={result}
              kind={data.tipo_equipo}
            />
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
    </>
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
        .catch((e) => active && setAvailability({ disponible: false, mensaje: e.message }));
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
        top_n: 5,
        contexto_previo: pending.context || undefined,
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
            ? { tipo_equipo: data.tipo_equipo, requisitos: data.requisitos }
            : pending.context,
        // Diez turnos por consulta mantienen el historial útil sin agotar
        // el almacenamiento local con respuestas técnicas extensas.
        messages: [...pending.messages, assistant].slice(-20),
      };
      updateChat(completed);
      if (data.estado === "no_disponible")
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
          IA limitada · Capa gratuita · {availability?.disponible ? "Disponible ahora" : "No disponible"}
        </span>
      </div>

      {!availability?.disponible && availability && (
        <div className="notice error">
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
            navegador.
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
                    context: undefined,
                  })
                }
              >
                <option value="auto">Detectar automáticamente</option>
                <option value="gnss">Receptor GNSS</option>
                <option value="controladora">Controladora</option>
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

          <div className="ai-messages" aria-live="polite">
            {!active?.messages.length && (
              <div className="ai-welcome">
                <Bot size={38} />
                <h2>¿Qué equipo necesitas?</h2>
                <p>
                  Por ejemplo: “Busco un GNSS con dos cámaras, láser, radio
                  interna y al menos 12 horas de autonomía”.
                </p>
              </div>
            )}
            {active?.messages.map((item) => (
              <article className={`ai-message ${item.role}`} key={item.id}>
                <div className="ai-message-label">
                  {item.role === "user" ? "Tú" : "Lici"}
                </div>
                {item.role === "assistant" ? (
                  <AssistantAnswer data={item.data} />
                ) : (
                  <p>{item.text}</p>
                )}
              </article>
            ))}
            {busy && (
              <div className="ai-message assistant">
                <div className="ai-message-label">Lici</div>
                <p>Interpretando requisitos y calculando el ranking…</p>
              </div>
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
            técnicos de Licitex. Confirma ficha, accesorios y condiciones de la
            oferta. No ingreses información confidencial mientras uses el nivel
            gratuito.
          </p>
          <details className="ai-error-legend">
            <summary>Qué significan los códigos de error de la IA</summary>
            <dl>
              <div><dt>400</dt><dd>La consulta no tuvo un formato aceptado por el proveedor.</dd></div>
              <div><dt>401 / 403</dt><dd>La clave no es válida o no tiene permiso para usar el modelo.</dd></div>
              <div><dt>404</dt><dd>El modelo configurado no existe o dejó de estar disponible.</dd></div>
              <div><dt>429</dt><dd>Se alcanzó la cuota gratuita o el límite temporal de consultas.</dd></div>
              <div><dt>500</dt><dd>El proveedor tuvo un error interno.</dd></div>
              <div><dt>502 / 503 / 504</dt><dd>Falla temporal, saturación o demora del proveedor; Licitex reintenta automáticamente.</dd></div>
            </dl>
          </details>
        </section>
      </div>
    </main>
  );
}
