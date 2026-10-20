import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "./api";
import { usePersistentState } from "./persist";

type Campo = {
  clave: string;
  nombre: string;
  tipo: "boolean" | "number" | "text";
  unidad: string;
  modo: "min" | "max" | "yes" | "ip" | "contains" | null;
  opciones: (string | number | boolean)[];
};

function useCampos() {
  const [campos, setCampos] = useState<Campo[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    api("/slam/campos")
      .then((data) => alive && setCampos(data))
      .catch((reason) => alive && setError(reason.message));
    return () => {
      alive = false;
    };
  }, []);
  return { campos, error };
}

function show(value: unknown) {
  return value == null || value === ""
    ? "Sin información"
    : typeof value === "boolean"
      ? value
        ? "Sí"
        : "No"
      : String(value);
}

function input(
  field: Campo,
  value: unknown,
  change: (value: unknown) => void,
  requirements = false,
) {
  const suffix = field.unidad ? ` (${field.unidad})` : "";
  const bound =
    requirements && field.tipo === "number"
      ? ` · ${field.modo === "min" ? "mínimo" : "máximo"}`
      : "";
  return (
    <label key={field.clave}>
      {field.nombre}
      {suffix}
      {bound}
      {field.tipo === "boolean" ? (
        <select
          value={value == null ? "" : String(value)}
          onChange={(event) =>
            change(
              event.target.value === "" ? null : event.target.value === "true",
            )
          }
        >
          <option value="">
            {requirements ? "Sin preferencia" : "Sin información"}
          </option>
          <option value="true">Sí</option>
          <option value="false">
            {requirements ? "No lo necesito" : "No"}
          </option>
        </select>
      ) : requirements ? (
        <select
          value={(value as string | number | undefined) ?? ""}
          onChange={(event) =>
            change(
              event.target.value === ""
                ? null
                : field.tipo === "number"
                  ? Number(event.target.value)
                  : event.target.value,
            )
          }
        >
          <option value="">Sin preferencia</option>
          {field.opciones.map((option) => (
            <option key={String(option)} value={String(option)}>
              {String(option)}
              {field.unidad ? ` ${field.unidad}` : ""}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={field.tipo === "number" ? "number" : "text"}
          step="any"
          min={
            field.tipo === "number" && !field.clave.startsWith("temperatura_")
              ? 0
              : undefined
          }
          value={(value as string | number | undefined) ?? ""}
          onChange={(event) =>
            change(
              event.target.value === ""
                ? null
                : field.tipo === "number"
                  ? Number(event.target.value)
                  : event.target.value,
            )
          }
        />
      )}
    </label>
  );
}

export function SlamSpecs({
  data,
  id,
  onSaved,
  audit,
}: {
  data: any;
  id?: string;
  onSaved?: () => void;
  audit?: Record<string, any>;
}) {
  const { campos, error } = useCampos();
  const [draft, setDraft] = useState<any>(data || {});
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => setDraft(data || {}), [data]);

  async function save(event: FormEvent) {
    event.preventDefault();
    const changes = Object.fromEntries(
      campos
        .filter(
          (field) =>
            (draft[field.clave] ?? null) !== (data?.[field.clave] ?? null),
        )
        .map((field) => [field.clave, draft[field.clave] ?? null]),
    );
    if (!Object.keys(changes).length) {
      setMessage("Modifica al menos una especificación antes de guardar.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      await api(`/admin/equipos/${id}/slam`, "PATCH", { cambios: changes });
      setMessage("Especificaciones SLAM guardadas.");
      onSaved?.();
    } catch (reason) {
      setMessage((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Características del escáner SLAM</h2>
      {error && <p role="alert">{error}</p>}
      {id ? (
        <form onSubmit={save}>
          <p className="muted">
            Solo se guardan los campos modificados. Deja sin información lo que
            la ficha no declare y distingue los módulos opcionales del hardware
            integrado.
          </p>
          <fieldset disabled={busy}>
            <div className="form-grid">
              {campos.map((field) =>
                input(field, draft[field.clave], (next) =>
                  setDraft({ ...draft, [field.clave]: next }),
                ),
              )}
            </div>
            <button disabled={busy || !campos.length}>
              {busy ? "Guardando…" : "Guardar especificaciones SLAM"}
            </button>
          </fieldset>
          <p role="status">{message}</p>
        </form>
      ) : (
        <dl>
          {campos.map((field) => (
            <div key={field.clave}>
              <dt>{field.nombre}</dt>
              <dd>
                {data?.[field.clave] == null
                  ? audit?.[`slam_${field.clave}`]?.etiqueta ||
                    "No publicado / pendiente de confirmar"
                  : show(data[field.clave])}
                {data?.[field.clave] != null && field.unidad
                  ? ` ${field.unidad}`
                  : ""}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}

export function SlamRank({ slot }: { slot: string }) {
  const { campos, error } = useCampos();
  const [draft, setDraft] = usePersistentState<any>(
    `licitex-slam-form-${slot}`,
    { solo_cotecmi: true },
  );
  const [result, setResult] = usePersistentState<any>(
    `licitex-slam-resultado-${slot}`,
    null,
  );
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      setResult(
        await api("/slam/recomendar", "POST", {
          requisitos: Object.fromEntries(
            Object.entries(draft).filter(([key]) => key !== "solo_cotecmi"),
          ),
          solo_cotecmi: draft.solo_cotecmi !== false,
          top_n: 100,
        }),
      );
    } catch (reason) {
      setMessage((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="container">
      <div className="grid recommend-grid">
        <section className="panel">
          <h2>Recomendador de escáneres SLAM</h2>
          <p className="muted">
            Indica la aplicación y los mínimos del pliego. El ranking distingue
            GNSS integrado de módulos opcionales, compara la precisión bajo las
            condiciones declaradas y marca como «sin información» lo que la
            ficha no confirma.
          </p>
          {error && <p role="alert">{error}</p>}
          <form onSubmit={submit}>
            <label>
              Equipos a evaluar
              <select
                value={String(draft.solo_cotecmi !== false)}
                onChange={(event) =>
                  setDraft({
                    ...draft,
                    solo_cotecmi: event.target.value === "true",
                  })
                }
              >
                <option value="true">Solo Cotecmi</option>
                <option value="false">Cotecmi y competencia</option>
              </select>
            </label>
            <fieldset disabled={busy}>
              <div className="form-grid">
                {campos
                  .filter((field) => field.modo)
                  .map((field) =>
                    input(
                      field,
                      draft[field.clave],
                      (next) => setDraft({ ...draft, [field.clave]: next }),
                      true,
                    ),
                  )}
              </div>
              <div className="links">
                <button disabled={busy || !campos.length}>
                  {busy ? "Calculando…" : "Buscar escáneres SLAM"}
                </button>
                <button
                  type="button"
                  className="outline"
                  onClick={() => {
                    setDraft({ solo_cotecmi: true });
                    setResult(null);
                  }}
                >
                  Limpiar
                </button>
              </div>
            </fieldset>
            <p role="alert">{message}</p>
          </form>
        </section>
        <section>
          {!result ? (
            <p>Completa al menos un requisito para obtener el ranking.</p>
          ) : (
            <>
              <p>{result.total_equipos} escáneres SLAM evaluados</p>
              {result.resultados.map((item: any) => (
                <article
                  className="panel rank-card"
                  key={item.equipo.id_equipo}
                >
                  <div className="rank-heading">
                    <span className="rank-number">
                      #{item.posicion}
                      {item.empate ? " · Empate" : ""}
                    </span>
                    <Link to={`/equipos/${item.equipo.id_equipo}`}>
                      <h3>
                        {item.equipo.marca} {item.equipo.modelo}
                      </h3>
                    </Link>
                    <strong>{item.porcentaje}% de ajuste</strong>
                  </div>
                  <progress max={100} value={item.porcentaje} />
                  <p>
                    {item.cumplimientos} requisitos cumplidos · {item.sin_datos}{" "}
                    sin información ·{" "}
                    {item.detalle.length - item.cumplimientos - item.sin_datos}{" "}
                    no cumplidos
                  </p>
                  <details className="score-details">
                    <summary>Ver criterios evaluados</summary>
                    <dl>
                      {item.detalle.map((detail: any) => (
                        <div key={detail.clave}>
                          <dt>{detail.nombre}</dt>
                          <dd>
                            {detail.estado === "cumple"
                              ? "Cumple"
                              : detail.estado === "sin_datos"
                                ? "Sin información"
                                : "No cumple"}{" "}
                            · {show(detail.valor)} {detail.unidad} · Requerido:{" "}
                            {show(detail.requerido)}
                          </dd>
                        </div>
                      ))}
                    </dl>
                  </details>
                </article>
              ))}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
