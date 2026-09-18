import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "./api";
import { usePersistentState } from "./persist";

type Campo = {
  clave: string;
  nombre: string;
  tipo: string;
  unidad: string;
  modo: string | null;
  opciones: (string | number | boolean)[];
};
function useCampos() {
  const [campos, setCampos] = useState<Campo[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    api("/controladoras/campos")
      .then((d) => {
        if (alive) setCampos(d);
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, []);
  return { campos, error };
}
function value(v: any) {
  return v == null
    ? "Sin información"
    : typeof v === "boolean"
      ? v
        ? "Sí"
        : "No"
      : String(v);
}
function input(
  c: Campo,
  v: any,
  onChange: (v: any) => void,
  requirements = false,
) {
  return (
    <label key={c.clave}>
      {c.nombre}
      {c.unidad ? ` (${c.unidad})` : ""}
      {requirements && c.tipo === "number"
        ? ` · ${c.modo === "min" ? "mínimo" : "máximo"}`
        : ""}
      {c.tipo === "boolean" ? (
        <select
          value={v == null ? "" : String(v)}
          onChange={(e) =>
            onChange(e.target.value === "" ? null : e.target.value === "true")
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
          value={v ?? ""}
          onChange={(e) =>
            onChange(
              e.target.value === ""
                ? null
                : c.tipo === "number"
                  ? Number(e.target.value)
                  : e.target.value,
            )
          }
        >
          <option value="">Sin preferencia</option>
          {c.opciones.map((option) => (
            <option key={String(option)} value={String(option)}>
              {String(option)}
              {c.unidad ? " " + c.unidad : ""}
            </option>
          ))}
        </select>
      ) : (
        <input
          type={c.tipo === "number" ? "number" : "text"}
          step="any"
          min={
            c.tipo === "number" && !c.clave.startsWith("temperatura_")
              ? 0
              : undefined
          }
          value={v ?? ""}
          onChange={(e) =>
            onChange(
              e.target.value === ""
                ? null
                : c.tipo === "number"
                  ? Number(e.target.value)
                  : e.target.value,
            )
          }
        />
      )}
    </label>
  );
}
export function ControllerSpecs({
  data,
  id,
  onSaved,
}: {
  data: any;
  id?: string;
  onSaved?: () => void;
}) {
  const { campos, error } = useCampos();
  const [draft, setDraft] = useState<any>(data || {}),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  useEffect(() => setDraft(data || {}), [data]);
  async function save(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const cambios = Object.fromEntries(
        campos.map((c) => [c.clave, draft[c.clave] ?? null]),
      );
      await api("/admin/equipos/" + id + "/controladora", "PATCH", { cambios });
      setMessage("Especificaciones guardadas.");
      onSaved?.();
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="panel">
      <h2>Características de la controladora</h2>
      {error && <p role="alert">{error}</p>}
      {id ? (
        <form onSubmit={save}>
          <p className="muted">
            Deja vacío lo que no esté declarado en la ficha. Los campos incluyen
            características habituales de licitaciones.
          </p>
          <fieldset disabled={busy}>
            <div className="form-grid">
              {campos.map((c) =>
                input(c, draft[c.clave], (v) =>
                  setDraft({ ...draft, [c.clave]: v }),
                ),
              )}
            </div>
            <button disabled={busy || !campos.length}>
              {busy ? "Guardando…" : "Guardar controladora"}
            </button>
          </fieldset>
          <p role="status">{message}</p>
        </form>
      ) : (
        <dl>
          {campos.map((c) => (
            <div key={c.clave}>
              <dt>{c.nombre}</dt>
              <dd>
                {value(data?.[c.clave])}
                {data?.[c.clave] != null && c.unidad ? " " + c.unidad : ""}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}
export function ControllerRank({ slot }: { slot: string }) {
  const { campos, error } = useCampos();
  const [draft, setDraft] = usePersistentState<any>(
    "licitex-controladora-form-" + slot,
    {},
  );
  const [result, setResult] = usePersistentState<any>(
    "licitex-controladora-resultado-" + slot,
    null,
  );
  const [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      setResult(
        await api("/controladoras/recomendar", "POST", {
          requisitos: draft,
          top_n: 100,
        }),
      );
    } catch (e) {
      setMessage((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="grid recommend-grid">
      <section className="panel">
        <h2>Ranking de controladoras</h2>
        <p className="muted">
          Solo puntúan los requisitos indicados, con el mismo peso provisional.
          Seleccionar «No lo necesito» omite ese criterio. La autonomía se
          compara según lo declarado; revisa las condiciones de cada ficha. Los
          códigos IP se comparan exactamente.
        </p>
        {error && <p role="alert">{error}</p>}
        <form onSubmit={submit}>
          <fieldset disabled={busy}>
            <div className="form-grid">
              {campos
                .filter((c) => c.modo)
                .map((c) =>
                  input(
                    c,
                    draft[c.clave],
                    (v) => setDraft({ ...draft, [c.clave]: v }),
                    true,
                  ),
                )}
            </div>
            <div className="links">
              <button disabled={busy || !campos.length}>
                {busy ? "Calculando…" : "Buscar controladoras"}
              </button>
              <button
                type="button"
                className="outline"
                onClick={() => {
                  setDraft({});
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
          <p>Completa tus requisitos para obtener el ranking.</p>
        ) : (
          <>
            <p>{result.total_equipos} controladoras evaluadas</p>
            {result.resultados.map((r: any) => (
              <article className="panel" key={r.equipo.id_equipo}>
                <div className="rank-heading">
                  <span className="rank-number">
                    #{r.posicion}
                    {r.empate ? " · Empate" : ""}
                  </span>
                  <Link to={"/equipos/" + r.equipo.id_equipo}>
                    <h3>
                      {r.equipo.marca} {r.equipo.modelo}
                    </h3>
                  </Link>
                  <strong>{r.porcentaje}% de ajuste</strong>
                </div>
                <progress max={100} value={r.porcentaje} />
                <p>
                  {r.cumplimientos} requisitos cumplidos · {r.sin_datos} sin
                  información ·{" "}
                  {r.detalle.length - r.cumplimientos - r.sin_datos} no
                  cumplidos
                </p>
                <details className="score-details">
                  <summary>Ver criterios evaluados</summary>
                  <dl>
                    {r.detalle.map((d: any) => (
                      <div key={d.clave}>
                        <dt>{d.nombre}</dt>
                        <dd>
                          {d.estado === "cumple"
                            ? "Cumple"
                            : d.estado === "sin_datos"
                              ? "Sin información"
                              : "No cumple"}{" "}
                          · {value(d.valor)} {d.unidad} · Requerido:{" "}
                          {value(d.requerido)}
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
  );
}
