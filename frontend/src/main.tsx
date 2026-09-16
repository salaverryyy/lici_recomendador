import React, {
  useEffect,
  useState,
  useRef,
  createContext,
  useContext,
  type FormEvent,
  type ReactNode,
} from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  NavLink,
  useNavigate,
  useLocation,
  useParams,
  useSearchParams,
} from "react-router-dom";
import {
  Compass,
  Search,
  SlidersHorizontal,
  Scale,
  ArrowRight,
  LockKeyhole,
  ImageOff,
  Plus,
  X,
  Check,
  Upload,
  LogOut,
} from "lucide-react";
import { api, setCsrf } from "./api";
import "./style.css";

type Equipo = {
  id_equipo: string;
  marca: string;
  modelo: string;
  categoria: string;
  imagen_url?: string;
  [key: string]: any;
};
type Columna = {
  clave: string;
  nombre: string;
  unidad?: string;
  valores?: Record<string, any>;
};
const Selection = createContext<{
  ids: string[];
  toggle: (id: string) => void;
}>({ ids: [], toggle: () => {} });
const label = (key: string) =>
  key.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase());
function valor(v: any): string {
  return v === null || v === undefined
    ? "Sin datos"
    : typeof v === "boolean"
      ? v
        ? "Sí"
        : "No"
      : Array.isArray(v)
        ? v.map((r) => `${r.min_mhz}–${r.max_mhz}`).join(" / ") || "Sin datos"
        : String(v);
}
function useData(url: string) {
  const previousUrl = useRef(url);
  const [data, setData] = useState<any>(null),
    [error, setError] = useState(""),
    [version, setVersion] = useState(0);
  useEffect(() => {
    let alive = true;
    if (previousUrl.current !== url) {
      setData(null);
      previousUrl.current = url;
    }
    setError("");
    api(url)
      .then((d) => {
        if (alive) setData(d);
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [url, version]);
  return { data, error, reload: () => setVersion((v) => v + 1) };
}
function Feedback({ error, loading }: { error?: string; loading?: boolean }) {
  return error ? (
    <div role="alert" className="notice error">
      {error}
    </div>
  ) : loading ? (
    <div role="status" className="notice">
      Cargando…
    </div>
  ) : null;
}
function Action({
  children,
  onSubmit,
  success = "Cambios guardados.",
}: {
  children: ReactNode;
  onSubmit: (form: HTMLFormElement) => Promise<unknown>;
  success?: string;
}) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState("");
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await onSubmit(form);
      if (result !== false) setMessage(success);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      <Feedback error={error} />
      {message && (
        <div role="status" className="notice success">
          {message}
        </div>
      )}
      <fieldset disabled={busy}>{children}</fieldset>
      {busy && <p role="status">Guardando…</p>}
    </form>
  );
}
const fields = (f: HTMLFormElement) =>
  Object.fromEntries(new FormData(f)) as Record<string, string>;
function Field({
  name,
  title,
  type = "text",
  required = false,
  value = "",
  min,
  max,
}: {
  name: string;
  title: string;
  type?: string;
  required?: boolean;
  value?: string | number;
  min?: number;
  max?: number;
}) {
  return (
    <label>
      {title}
      <input
        name={name}
        type={type}
        required={required}
        defaultValue={value}
        min={min}
        max={max}
        minLength={
          name === "nueva_contrasena" || name === "confirmar_contrasena"
            ? 12
            : undefined
        }
        step={type === "number" ? "any" : undefined}
      />
    </label>
  );
}
function Photo({ url, alt }: { url?: string; alt: string }) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [url]);
  return url && !failed ? (
    <img src={url} alt={alt} loading="lazy" onError={() => setFailed(true)} />
  ) : (
    <div className="no-photo">
      <ImageOff size={32} />
      <span>Fotografía pendiente</span>
    </div>
  );
}
function CompareButton({ id }: { id: string }) {
  const { ids, toggle } = useContext(Selection);
  return (
    <button
      type="button"
      className={"select-btn " + (ids.includes(id) ? "selected" : "")}
      onClick={() => toggle(id)}
    >
      {ids.includes(id) ? <Check size={15} /> : <Plus size={15} />} Comparar
    </button>
  );
}
function Card({ equipo }: { equipo: Equipo }) {
  return (
    <article className="equipment-card">
      <Link className="photo" to={"/equipos/" + equipo.id_equipo}>
        <Photo
          url={equipo.imagen_url}
          alt={`${equipo.marca} ${equipo.modelo}`}
        />
      </Link>
      <div className="card-body">
        <span className="eyebrow">{equipo.categoria}</span>
        <h3>
          {equipo.marca} {equipo.modelo}
        </h3>
        <div className="tags">
          {equipo.canales_gnss != null && (
            <span>{equipo.canales_gnss} canales</span>
          )}
          {equipo.tiene_imu === true && <span className="teal">IMU</span>}
          {equipo.peso_max != null && <span>{equipo.peso_max} g</span>}
        </div>
        <div className="card-actions">
          <CompareButton id={equipo.id_equipo} />
          <Link className="outline small" to={"/equipos/" + equipo.id_equipo}>
            Ver ficha <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </article>
  );
}
function Home() {
  const [q, setQ] = useState(""),
    navigate = useNavigate();
  return (
    <>
      <section className="hero">
        <div className="container">
          <span className="pill">Tu próximo equipo empieza aquí</span>
          <h1>
            Elige con información.
            <br />
            <em>Encuentra con Licitex.</em>
          </h1>
          <p>
            Consulta especificaciones, compara equipos y descubre cuáles se
            ajustan a lo que necesitas.
          </p>
          <form
            className="search-box"
            onSubmit={(e) => {
              e.preventDefault();
              navigate("/catalogo?q=" + encodeURIComponent(q));
            }}
          >
            <Search size={20} />
            <input
              aria-label="Buscar equipo o marca"
              placeholder="¿Qué marca o modelo buscas?"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <button>Buscar</button>
          </form>
        </div>
      </section>
      <section className="container home-tools">
        <span className="eyebrow">DEL DATO A LA DECISIÓN</span>
        <h2>Tres formas de encontrar tu equipo</h2>
        <p className="muted">Explora a tu ritmo. Compara lo que importa.</p>
        <div className="grid three">
          {[
            [
              "/catalogo",
              "Catálogo técnico",
              "Especificaciones y fichas de los equipos, en un solo lugar.",
              Compass,
            ],
            [
              "/comparar",
              "Comparador",
              "Pon tus opciones lado a lado y elige qué características ver.",
              Scale,
            ],
            [
              "/recomendador",
              "Recomendador",
              "Indica tus requisitos y revisa un ranking con sus motivos.",
              SlidersHorizontal,
            ],
          ].map(([url, title, text, Icon]: any) => (
            <Link className="tool-card" to={url} key={url}>
              <Icon size={26} />
              <h3>{title}</h3>
              <p>{text}</p>
              <span>
                Explorar <ArrowRight size={17} />
              </span>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
function Catalog() {
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get("q") || "");
  const { data, error } = useData("/equipos?" + params.toString()),
    options = useData("/equipos/opciones");
  function change(key: string, value: string) {
    const p = new URLSearchParams(params);
    value ? p.set(key, value) : p.delete(key);
    setParams(p);
  }
  return (
    <main className="container">
      <div className="page-title">
        <div>
          <span className="eyebrow">EXPLORA TUS OPCIONES</span>
          <h1>Catálogo de equipos</h1>
          <p className="muted">
            Información técnica para elegir con confianza.
          </p>
        </div>
        {data && <span className="count">{data.length} equipos</span>}
      </div>
      <section className="panel filters">
        <form
          className="search-box"
          onSubmit={(e) => {
            e.preventDefault();
            change("q", q);
          }}
        >
          <Search size={18} />
          <input
            aria-label="Buscar"
            placeholder="Buscar por modelo o marca…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <button>Buscar</button>
        </form>
        <div className="grid three">
          {["marca", "categoria"].map((key) => (
            <label key={key}>
              {label(key)}
              <select
                value={params.get(key) || ""}
                onChange={(e) => change(key, e.target.value)}
              >
                <option value="">Todas</option>
                {options.data?.[key === "marca" ? "marcas" : "categorias"].map(
                  (v: string) => (
                    <option key={v}>{v}</option>
                  ),
                )}
              </select>
            </label>
          ))}
          <label>
            Ordenar por
            <select
              value={params.get("orden") || "marca"}
              onChange={(e) => change("orden", e.target.value)}
            >
              {[
                ["marca", "Marca"],
                ["modelo", "Modelo"],
                ["anio_desc", "Más recientes"],
                ["canales_desc", "Más canales"],
                ["peso_asc", "Menor peso"],
              ].map(([v, l]) => (
                <option value={v} key={v}>
                  {l}
                </option>
              ))}
            </select>
          </label>
        </div>
        <Feedback error={options.error} />
      </section>
      <Feedback error={error} loading={!data && !error} />
      {data?.length === 0 && (
        <section className="empty">
          <Search />
          <h2>No encontramos equipos</h2>
          <p>Prueba con otra búsqueda o limpia los filtros.</p>
          <button
            onClick={() => {
              setQ("");
              setParams({});
            }}
          >
            Limpiar filtros
          </button>
        </section>
      )}
      <div className="grid three">
        {data?.map((e: Equipo) => (
          <Card equipo={e} key={e.id_equipo} />
        ))}
      </div>
    </main>
  );
}
function Detail() {
  const { id } = useParams(),
    { data, error } = useData("/equipos/" + id),
    columns = useData("/comparar/columnas");
  const [selected, setSelected] = useState("");
  if (!data)
    return (
      <main className="container">
        <Feedback error={error} loading={!error} />
      </main>
    );
  const e = data.equipo,
    fotos = data.fotografias || [],
    photo =
      fotos.find((f: any) => String(f.id) === selected)?.url || e.imagen_url;
  return (
    <main className="container">
      <Link className="back" to="/catalogo">
        ← Volver al catálogo
      </Link>
      <div className="grid detail-grid">
        <section>
          <div className="detail-photo">
            <Photo url={photo} alt={`${e.marca} ${e.modelo}`} />
          </div>
          <div className="thumbnails">
            {fotos.map((f: any) => (
              <button
                aria-label={f.texto_alternativo || "Ver foto"}
                key={f.id}
                onClick={() => setSelected(String(f.id))}
              >
                <Photo url={f.url} alt={f.texto_alternativo || e.modelo} />
              </button>
            ))}
          </div>
          <div className="links">
            {e.ficha_pdf_url && (
              <a
                className="outline"
                href={e.ficha_pdf_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Ficha técnica PDF ↗
              </a>
            )}
            {e.web_url && (
              <a
                className="outline"
                href={e.web_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Web del fabricante ↗
              </a>
            )}
          </div>
          <CompareButton id={e.id_equipo} />
        </section>
        <section>
          <span className="eyebrow">
            {e.categoria} · {e.marca}
          </span>
          <h1>{e.modelo}</h1>
          {e.descripcion && <p>{e.descripcion}</p>}
          <div className="panel">
            <h3>Especificaciones técnicas</h3>
            <Feedback error={columns.error} />
            <dl>
              {columns.data
                ?.filter(
                  (c: Columna) =>
                    !["marca", "modelo", "categoria", "radio_rangos"].includes(
                      c.clave,
                    ),
                )
                .map((c: Columna) => (
                  <div key={c.clave}>
                    <dt>
                      {c.nombre}
                      {c.unidad ? " (" + c.unidad + ")" : ""}
                    </dt>
                    <dd>{valor(e[c.clave] ?? data.evaluacion?.[c.clave])}</dd>
                  </div>
                ))}
              <div>
                <dt>Rangos de radio (MHz)</dt>
                <dd>
                  {data.radio_frecuencias
                    .map(
                      (r: any) =>
                        `${r.frecuencia_min_mhz}–${r.frecuencia_max_mhz}`,
                    )
                    .join(" / ") || "Sin datos"}
                </dd>
              </div>
            </dl>
          </div>
          {e.modelo_3d_url && (
            <a
              className="outline"
              href={e.modelo_3d_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Abrir modelo 3D ↗
            </a>
          )}
        </section>
      </div>
    </main>
  );
}
function Compare() {
  const { ids, toggle } = useContext(Selection),
    metadata = useData("/comparar/columnas");
  const [columns, setColumns] = useState([
      "tiene_imu",
      "tiene_camara",
      "canales_gnss",
      "constelaciones",
      "rtk_horizontal_mm",
      "rtk_vertical_mm",
      "autonomia_bateria",
      "peso_max",
      "radio_rangos",
    ]),
    [hide, setHide] = useState(false);
  const { data, error } = useData(
    ids.length >= 2
      ? "/comparar?ids=" + ids.join(",") + "&columnas=" + columns.join(",")
      : "/comparar/columnas",
  );
  return (
    <main className="container">
      <div className="page-title">
        <div>
          <span className="eyebrow">UNA DECISIÓN, TODOS LOS DATOS</span>
          <h1>Comparador de equipos</h1>
          <p className="muted">
            Selecciona las características que quieres comparar.
          </p>
        </div>
        <Link className="button" to="/catalogo">
          <Plus size={16} /> Añadir equipos
        </Link>
      </div>
      {ids.length < 2 ? (
        <section className="empty">
          <Scale size={40} />
          <h2>Elige al menos dos equipos</h2>
          <p>Márcalos desde el catálogo para verlos lado a lado.</p>
          <Link className="button" to="/catalogo">
            Explorar catálogo
          </Link>
        </section>
      ) : (
        <>
          <details className="panel">
            <summary>Características visibles ({columns.length})</summary>
            <div className="checks">
              {metadata.data?.map((c: Columna) => (
                <label key={c.clave}>
                  <input
                    type="checkbox"
                    checked={columns.includes(c.clave)}
                    disabled={columns.length === 1 && columns.includes(c.clave)}
                    onChange={() =>
                      setColumns((v) =>
                        v.includes(c.clave)
                          ? v.filter((k) => k !== c.clave)
                          : [...v, c.clave],
                      )
                    }
                  />
                  {c.nombre} {c.unidad}
                </label>
              ))}
            </div>
          </details>
          <label className="inline">
            <input
              type="checkbox"
              checked={hide}
              onChange={(e) => setHide(e.target.checked)}
            />{" "}
            Ocultar características iguales
          </label>
          <Feedback error={error} loading={!data && !error} />
          {data?.equipos && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Característica</th>
                    {data.equipos.map((e: Equipo) => (
                      <th key={e.id_equipo}>
                        <Link to={"/equipos/" + e.id_equipo}>
                          {e.marca} {e.modelo}
                        </Link>
                        <button
                          className="icon"
                          aria-label={"Quitar " + e.modelo}
                          onClick={() => toggle(e.id_equipo)}
                        >
                          <X size={16} />
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.columnas
                    .filter(
                      (c: Columna) =>
                        !hide ||
                        new Set(
                          Object.values(c.valores!).map((v) =>
                            JSON.stringify(v),
                          ),
                        ).size > 1,
                    )
                    .map((c: Columna) => (
                      <tr key={c.clave}>
                        <th>
                          {c.nombre} {c.unidad && <small>({c.unidad})</small>}
                        </th>
                        {ids.map((id) => (
                          <td key={id}>{valor(c.valores?.[id])}</td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </main>
  );
}
function Recommend() {
  const metadata = useData("/recomendador/criterios"),
    [result, setResult] = useState<any>(null);
  const unique = metadata.data?.criterios
    .filter((c: any) => c.activo)
    .filter(
      (c: any, i: number, all: any[]) =>
        all.findIndex((x) => x.campo_input === c.campo_input) === i,
    );
  return (
    <main className="container">
      <div className="page-title">
        <div>
          <span className="eyebrow">ENCUENTRA CON LICI</span>
          <h1>Recomendador de equipos</h1>
          <p className="muted">
            Completa solo lo que necesitas. Los demás campos pueden quedar
            vacíos.
          </p>
        </div>
      </div>
      <div className="grid recommend-grid">
        <section className="panel">
          <Feedback
            error={metadata.error}
            loading={!metadata.data && !metadata.error}
          />
          <Action
            success="Ranking actualizado."
            onSubmit={async (f) => {
              setResult(null);
              const values = fields(f);
              const body: Record<string, any> = {};
              Object.entries(values).forEach(([k, v]) => {
                if (v !== "")
                  body[k] =
                    v === "true" ? true : v === "false" ? false : Number(v);
              });
              setResult(await api("/recomendar", "POST", body));
            }}
          >
            <h3>Tus requisitos</h3>
            <p className="muted small-text">
              «No» significa que no lo necesitas. Ningún equipo se descarta: el
              cumplimiento determina la puntuación.
            </p>
            <div className="form-grid">
              {unique?.map((c: any) =>
                c.modo === "booleano" ? (
                  <label key={c.clave}>
                    {c.nombre}
                    <select name={c.campo_input}>
                      <option value="">Sin preferencia</option>
                      <option value="true">Sí, lo necesito</option>
                      <option value="false">No lo necesito</option>
                    </select>
                  </label>
                ) : c.modo === "radio" ? (
                  <React.Fragment key={c.clave}>
                    <Field
                      name="radio_min_mhz"
                      title="Radio mínima (MHz)"
                      type="number"
                      min={0}
                    />
                    <Field
                      name="radio_max_mhz"
                      title="Radio máxima (MHz)"
                      type="number"
                      min={0}
                    />
                  </React.Fragment>
                ) : c.modo === "dimensiones" ? (
                  <React.Fragment key={c.clave}>
                    {["largo", "ancho", "alto"].map((k) => (
                      <Field
                        key={k}
                        name={k + "_max_mm"}
                        title={label(k) + " máximo (mm)"}
                        type="number"
                        min={0}
                      />
                    ))}
                  </React.Fragment>
                ) : (
                  <Field
                    key={c.clave}
                    name={c.campo_input}
                    title={`${c.campo_input === "rtk_ppm_max" ? "RTK horizontal y vertical" : c.campo_input === "static_ppm_max" ? "Estático horizontal y vertical" : c.nombre} ${c.modo === "minimo" ? "mínimo" : "máximo"}${c.unidad ? " (" + c.unidad + ")" : ""}`}
                    type="number"
                    min={c.clave === "constelaciones" ? 1 : 0}
                    max={c.clave === "constelaciones" ? 6 : undefined}
                  />
                ),
              )}
            </div>
            <Field
              name="top_n"
              title="Cantidad de resultados (1–100)"
              type="number"
              value={3}
              required
              min={1}
              max={100}
            />
            <div className="links">
              <button
                type="reset"
                className="outline"
                onClick={() => setResult(null)}
              >
                Limpiar
              </button>
              <button>Buscar equipos</button>
            </div>
          </Action>
        </section>
        <section>
          {!result ? (
            <div className="empty">
              <SlidersHorizontal size={38} />
              <h2>Tu ranking aparecerá aquí</h2>
              <p>Empieza con un criterio, por ejemplo IMU.</p>
            </div>
          ) : (
            <>
              <div className="page-title">
                <h2>Equipos recomendados</h2>
                <span className="count">
                  {result.mostrados} de {result.total_equipos}
                </span>
              </div>
              <p className="muted">
                El porcentaje indica ajuste a tus requisitos; los pesos aún son
                provisionales.
              </p>
              {result.resultados.map((r: any) => (
                <article className="panel rank-card" key={r.equipo.id_equipo}>
                  <div className="rank-heading">
                    <span className="rank-number">#{r.posicion}</span>
                    <Link to={"/equipos/" + r.equipo.id_equipo}>
                      <h3>
                        {r.equipo.marca} {r.equipo.modelo}
                      </h3>
                    </Link>
                    <strong>
                      {r.porcentaje == null
                        ? "Sin puntuación"
                        : r.porcentaje + "%"}
                    </strong>
                  </div>
                  {r.porcentaje != null && (
                    <progress max={100} value={r.porcentaje} />
                  )}
                  <p>{r.explicacion}</p>
                  <CompareButton id={r.equipo.id_equipo} />
                </article>
              ))}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
function Login() {
  const navigate = useNavigate();
  return (
    <main className="container narrow">
      <div className="panel">
        <LockKeyhole className="teal" />
        <h1>Administración</h1>
        <p className="muted">Accede para mantener el catálogo de Licitex.</p>
        <Action
          success="Sesión iniciada."
          onSubmit={async (f) => {
            const d = await api("/admin/login", "POST", fields(f));
            setCsrf(d.csrf_token);
            navigate("/admin/equipos");
          }}
        >
          <Field name="username" title="Usuario" required />
          <Field name="password" title="Contraseña" type="password" required />
          <button className="full">Iniciar sesión</button>
        </Action>
        <Link className="back" to="/recuperar-contrasena">
          ¿Olvidaste tu contraseña?
        </Link>
      </div>
    </main>
  );
}
function AdminLayout({ children }: { children: ReactNode }) {
  const session = useData("/admin/sesion"),
    navigate = useNavigate();
  useEffect(() => {
    if (session.data) setCsrf(session.data.csrf_token);
  }, [session.data]);
  useEffect(() => {
    const fn = () => navigate("/admin");
    window.addEventListener("sesion-expirada", fn);
    return () => window.removeEventListener("sesion-expirada", fn);
  }, [navigate]);
  return (
    <main className="container admin-shell">
      <div className="admin-nav">
        <NavLink to="/admin/equipos">Equipos</NavLink>
        <NavLink to="/admin/reglas">Pesos del ranking</NavLink>
        <NavLink to="/admin/cuenta">Mi cuenta</NavLink>
        <button
          className="outline"
          onClick={async () => {
            try {
              await api("/admin/logout", "POST");
              setCsrf("");
              navigate("/admin");
            } catch {
              navigate("/admin");
            }
          }}
        >
          <LogOut size={16} /> Salir
        </button>
      </div>
      <div className="admin-content">
        <Feedback
          error={session.error}
          loading={!session.data && !session.error}
        />
        {session.data && children}
      </div>
    </main>
  );
}
function AdminEquipment() {
  const { data, error, reload } = useData("/admin/equipos");
  return (
    <AdminLayout>
      <div className="page-title">
        <h1>Equipos</h1>
        <Link className="button" to="/admin/equipos/nuevo">
          <Plus size={17} /> Añadir equipo
        </Link>
      </div>
      <Feedback error={error} loading={!data && !error} />
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Equipo</th>
              <th>Categoría</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((e: Equipo) => (
              <tr key={e.id_equipo}>
                <td>
                  <strong>
                    {e.marca} {e.modelo}
                  </strong>
                  <small className="block">{e.id_equipo}</small>
                </td>
                <td>{e.categoria}</td>
                <td>{e.publicado ? "Publicado" : "Borrador"}</td>
                <td>
                  <Link
                    className="outline small"
                    to={"/admin/equipos/" + e.id_equipo}
                  >
                    Editar
                  </Link>
                  <Action
                    success="Equipo eliminado."
                    onSubmit={async () => {
                      if (
                        !window.confirm(
                          `¿Eliminar ${e.marca} ${e.modelo} y sus especificaciones y archivos?`,
                        )
                      )
                        return false;
                      await api("/admin/equipos/" + e.id_equipo, "DELETE");
                      reload();
                    }}
                  >
                    <button className="danger small">Eliminar</button>
                  </Action>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  );
}
function Editor() {
  const { id } = useParams(),
    isNew = id === "nuevo",
    navigate = useNavigate();
  const details = useData(
      isNew ? "/comparar/columnas" : "/admin/equipos/" + id,
    ),
    metadata = useData("/comparar/columnas"),
    files = useData(
      isNew ? "/comparar/columnas" : "/admin/equipos/" + id + "/archivos",
    );
  const e = isNew ? {} : details.data?.equipo;
  const bools = new Set([
    "tiene_imu",
    "tiene_camara",
    "sim_4g",
    "laser",
    "bateria_intercambiable",
    "bateria_caliente",
    "gps",
    "glonass",
    "galileo",
    "beidou",
    "qzss",
    "navic_irnss",
    "sbas",
  ]);
  const base = "/admin/equipos/" + id;
  return (
    <AdminLayout>
      <Link className="back" to="/admin/equipos">
        ← Volver a equipos
      </Link>
      <h1>{isNew ? "Añadir equipo" : "Editar equipo"}</h1>
      <Feedback error={details.error} />
      {e && (
        <>
          <section className="panel">
            <h2>Información general</h2>
            <Action
              key={JSON.stringify([
                e.id_equipo,
                e.marca,
                e.modelo,
                e.categoria,
                e.descripcion,
                e.anio_modelo,
                e.web_url,
                e.modelo_3d_url,
                e.publicado,
              ])}
              onSubmit={async (f) => {
                const d: Record<string, any> = fields(f);
                d.anio_modelo = d.anio_modelo ? Number(d.anio_modelo) : null;
                d.publicado = d.publicado === "true";
                ["descripcion", "web_url", "modelo_3d_url"].forEach(
                  (k) => (d[k] = d[k] || null),
                );
                const result = await api(
                  isNew ? "/admin/equipos" : base,
                  isNew ? "POST" : "PATCH",
                  d,
                );
                if (isNew) navigate("/admin/equipos/" + result.id_equipo);
                else details.reload();
              }}
            >
              <div className="form-grid">
                {isNew && (
                  <Field
                    name="id_equipo"
                    title="ID (letras mayúsculas, números y guiones)"
                    required
                  />
                )}
                {["marca", "modelo", "categoria"].map((k) => (
                  <Field
                    key={k}
                    name={k}
                    title={label(k)}
                    value={e[k] || (k === "categoria" ? "GNSS" : "")}
                    required
                  />
                ))}
                <Field
                  name="anio_modelo"
                  title="Año del modelo"
                  type="number"
                  value={e.anio_modelo || ""}
                  min={1900}
                  max={2200}
                />
                <label>
                  Estado
                  <select
                    name="publicado"
                    defaultValue={String(e.publicado ?? true)}
                  >
                    <option value="true">Publicado</option>
                    <option value="false">Borrador</option>
                  </select>
                </label>
                <Field
                  name="web_url"
                  title="Web del fabricante"
                  type="url"
                  value={e.web_url || ""}
                />
                <Field
                  name="modelo_3d_url"
                  title="Enlace al modelo 3D (opcional)"
                  type="url"
                  value={e.modelo_3d_url || ""}
                />
              </div>
              <label>
                Descripción
                <textarea
                  name="descripcion"
                  defaultValue={e.descripcion || ""}
                />
              </label>
              <button>Guardar información</button>
            </Action>
          </section>
          {!isNew && (
            <>
              <section className="panel">
                <h2>Fotografías y ficha técnica</h2>
                <p className="muted">
                  Fotos JPG, PNG o WebP (5 MB). Ficha PDF sin contraseña (20 MB
                  en local). Máximo 20 fotos por equipo.
                </p>
                <Feedback error={files.error} />
                <div className="grid three">
                  {files.data?.map((f: any) => (
                    <article className="media-card" key={f.id}>
                      {f.tipo === "foto" ? (
                        <Photo
                          url={f.url}
                          alt={f.texto_alternativo || e.modelo}
                        />
                      ) : (
                        <a
                          href={f.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Ver ficha PDF ↗
                        </a>
                      )}
                      <Action
                        onSubmit={async () => {
                          await api(base + "/archivos/" + f.id, "DELETE");
                          files.reload();
                          details.reload();
                        }}
                        success="Archivo eliminado."
                      >
                        <button className="danger small">
                          Quitar {f.tipo === "foto" ? "foto" : "ficha"}
                        </button>
                      </Action>
                      {f.tipo === "foto" && (
                        <>
                          <Action
                            success="Portada actualizada."
                            onSubmit={async () => {
                              await api(
                                base + "/archivos/" + f.id + "/portada",
                                "PUT",
                              );
                              details.reload();
                            }}
                          >
                            <button
                              className="outline small"
                              disabled={e.imagen_url === f.url}
                            >
                              {e.imagen_url === f.url
                                ? "Foto de portada"
                                : "Usar como portada"}
                            </button>
                          </Action>
                          <Action
                            onSubmit={async (form) => {
                              const d = fields(form);
                              await api(base + "/archivos/" + f.id, "PATCH", {
                                texto_alternativo: d.texto_alternativo,
                                orden: Number(d.orden),
                              });
                              files.reload();
                            }}
                          >
                            <Field
                              name="texto_alternativo"
                              title="Descripción de la foto"
                              value={f.texto_alternativo}
                            />
                            <Field
                              name="orden"
                              title="Orden"
                              type="number"
                              min={0}
                              value={f.orden}
                            />
                            <button className="outline small">
                              Guardar foto
                            </button>
                          </Action>
                        </>
                      )}
                    </article>
                  ))}
                </div>
                <div className="grid two">
                  <Action
                    success="Archivo cargado."
                    onSubmit={async (form) => {
                      const d = new FormData(form),
                        tipo = d.get("tipo");
                      d.delete("tipo");
                      await api(
                        base + "/archivos/subir?tipo=" + tipo,
                        "POST",
                        d,
                      );
                      form.reset();
                      files.reload();
                      details.reload();
                    }}
                  >
                    <h3>Cargar desde tu computadora</h3>
                    <label>
                      Tipo
                      <select name="tipo">
                        <option value="foto">Fotografía</option>
                        <option value="ficha">
                          Ficha técnica (reemplaza la anterior)
                        </option>
                      </select>
                    </label>
                    <label>
                      Archivo
                      <input
                        type="file"
                        name="archivo"
                        required
                        accept="image/jpeg,image/png,image/webp,application/pdf"
                      />
                    </label>
                    <button>
                      <Upload size={16} /> Cargar archivo
                    </button>
                  </Action>
                  <Action
                    onSubmit={async (form) => {
                      const d = fields(form);
                      await api(base + "/archivos/enlace", "POST", d);
                      form.reset();
                      files.reload();
                      details.reload();
                    }}
                  >
                    <h3>Añadir mediante URL</h3>
                    <label>
                      Tipo
                      <select name="tipo">
                        <option value="foto">Fotografía</option>
                        <option value="ficha">
                          Ficha PDF (reemplaza la anterior)
                        </option>
                      </select>
                    </label>
                    <Field name="url" title="URL pública" type="url" required />
                    <Field
                      name="texto_alternativo"
                      title="Descripción de la foto"
                    />
                    <button className="outline">Añadir enlace</button>
                  </Action>
                </div>
              </section>
              <section className="panel">
                <h2>Especificaciones técnicas</h2>
                <p className="muted">
                  Deja vacío si no hay datos. Constelaciones y disponibilidad
                  PPP se calculan automáticamente.
                </p>
                <Feedback error={metadata.error} />
                <Action
                  key={JSON.stringify(details.data.evaluacion)}
                  onSubmit={async (form) => {
                    const d = fields(form),
                      cambios: Record<string, any> = {};
                    Object.entries(d).forEach(([k, v]) => {
                      cambios[k] =
                        v === ""
                          ? null
                          : bools.has(k)
                            ? v === "true"
                            : k === "radio_frecuencia"
                              ? v
                              : Number(v);
                    });
                    await api(base + "/especificaciones", "PATCH", { cambios });
                    details.reload();
                  }}
                >
                  <div className="form-grid">
                    {metadata.data
                      ?.filter(
                        (c: Columna) =>
                          ![
                            "marca",
                            "modelo",
                            "categoria",
                            "anio_modelo",
                            "radio_rangos",
                            "constelaciones",
                            "tiene_ppp",
                          ].includes(c.clave),
                      )
                      .map((c: Columna) =>
                        bools.has(c.clave) ? (
                          <label key={c.clave}>
                            {c.nombre}
                            <select
                              name={c.clave}
                              defaultValue={
                                details.data.evaluacion?.[c.clave] == null
                                  ? ""
                                  : String(details.data.evaluacion[c.clave])
                              }
                            >
                              <option value="">Sin datos</option>
                              <option value="true">Sí</option>
                              <option value="false">No</option>
                            </select>
                          </label>
                        ) : (
                          <Field
                            key={c.clave}
                            name={c.clave}
                            title={
                              c.nombre + (c.unidad ? " (" + c.unidad + ")" : "")
                            }
                            type={
                              c.clave === "radio_frecuencia" ? "text" : "number"
                            }
                            min={0}
                            value={details.data.evaluacion?.[c.clave] ?? ""}
                          />
                        ),
                      )}
                  </div>
                  <button>Guardar especificaciones</button>
                </Action>
              </section>
              <section className="panel">
                <h2>Rangos de radio</h2>
                {details.data.radio_frecuencias.map((r: any) => (
                  <div key={r.id} className="radio-row">
                    <Action
                      onSubmit={async (form) => {
                        const d = fields(form);
                        await api(base + "/radio/" + r.id, "PUT", {
                          frecuencia_min_mhz: Number(d.frecuencia_min_mhz),
                          frecuencia_max_mhz: Number(d.frecuencia_max_mhz),
                        });
                        details.reload();
                      }}
                    >
                      <div className="form-grid">
                        <Field
                          name="frecuencia_min_mhz"
                          title="Mínima (MHz)"
                          type="number"
                          required
                          min={0}
                          value={r.frecuencia_min_mhz}
                        />
                        <Field
                          name="frecuencia_max_mhz"
                          title="Máxima (MHz)"
                          type="number"
                          required
                          min={0}
                          value={r.frecuencia_max_mhz}
                        />
                      </div>
                      <button className="outline small">Guardar rango</button>
                    </Action>
                    <Action
                      onSubmit={async () => {
                        await api(base + "/radio/" + r.id, "DELETE");
                        details.reload();
                      }}
                    >
                      <p>
                        {r.frecuencia_min_mhz}–{r.frecuencia_max_mhz} MHz{" "}
                        <button className="danger small">Quitar rango</button>
                      </p>
                    </Action>
                  </div>
                ))}
                <Action
                  onSubmit={async (f) => {
                    const d = fields(f);
                    await api(base + "/radio", "POST", {
                      frecuencia_min_mhz: Number(d.frecuencia_min_mhz),
                      frecuencia_max_mhz: Number(d.frecuencia_max_mhz),
                    });
                    f.reset();
                    details.reload();
                  }}
                >
                  <div className="form-grid">
                    <Field
                      name="frecuencia_min_mhz"
                      title="Mínima (MHz)"
                      type="number"
                      min={0}
                      required
                    />
                    <Field
                      name="frecuencia_max_mhz"
                      title="Máxima (MHz)"
                      type="number"
                      min={0}
                      required
                    />
                  </div>
                  <button className="outline">Añadir rango</button>
                </Action>
              </section>
            </>
          )}
        </>
      )}
    </AdminLayout>
  );
}
function Rules() {
  const { data, error, reload } = useData("/admin/reglas");
  return (
    <AdminLayout>
      <h1>Pesos del ranking</h1>
      <p className="muted">
        Solo los criterios que el usuario complete participan en la puntuación.
      </p>
      <Feedback error={error} />
      {data && (
        <Action
          onSubmit={async (f) => {
            const d = new FormData(f);
            await api(
              "/admin/reglas",
              "PUT",
              data.map((r: any) => ({
                criterio: r.criterio,
                peso: Number(d.get(r.criterio)),
                activo: d.has(r.criterio + "_activo"),
              })),
            );
            reload();
          }}
        >
          <div className="panel form-grid">
            {data.map((r: any) => (
              <div key={r.criterio}>
                <Field
                  name={r.criterio}
                  title={r.nombre}
                  type="number"
                  required
                  min={0}
                  max={1000}
                  value={r.peso}
                />
                <label className="inline">
                  <input
                    type="checkbox"
                    name={r.criterio + "_activo"}
                    defaultChecked={r.activo}
                  />
                  Activo
                </label>
              </div>
            ))}
          </div>
          <button>Guardar pesos</button>
        </Action>
      )}
    </AdminLayout>
  );
}
function Account() {
  const mails = useData("/admin/correos"),
    navigate = useNavigate();
  return (
    <AdminLayout>
      <h1>Mi cuenta</h1>
      <div className="grid two">
        <section className="panel">
          <h2>Correos de recuperación</h2>
          <Feedback error={mails.error} />
          {mails.data
            ?.filter((m: any) => m.activo)
            .map((m: any) => (
              <div className="mail-row" key={m.id}>
                <strong>{m.email}</strong>
                <p>
                  {m.es_principal ? "Principal · " : ""}
                  {m.verificado ? "Verificado" : "Pendiente de verificación"}
                </p>
                {!m.verificado && (
                  <Action
                    success="Revisa tu correo."
                    onSubmit={(f) =>
                      api(
                        "/admin/correos/" + m.id + "/enviar-verificacion",
                        "POST",
                        fields(f),
                      )
                    }
                  >
                    <Field
                      name="contrasena_actual"
                      title="Contraseña actual"
                      type="password"
                      required
                    />
                    <button className="outline small">
                      Enviar verificación
                    </button>
                  </Action>
                )}
                {m.verificado && !m.es_principal && (
                  <Action
                    onSubmit={async (f) => {
                      await api(
                        "/admin/correos/" + m.id + "/principal",
                        "PUT",
                        fields(f),
                      );
                      mails.reload();
                    }}
                  >
                    <Field
                      name="contrasena_actual"
                      title="Contraseña actual"
                      type="password"
                      required
                    />
                    <button className="outline small">
                      Usar como principal
                    </button>
                  </Action>
                )}
                {!m.es_principal && (
                  <Action
                    onSubmit={async (f) => {
                      await api("/admin/correos/" + m.id, "DELETE", fields(f));
                      mails.reload();
                    }}
                  >
                    <Field
                      name="contrasena_actual"
                      title="Contraseña actual"
                      type="password"
                      required
                    />
                    <button className="danger small">Quitar correo</button>
                  </Action>
                )}
              </div>
            ))}
          <Action
            onSubmit={async (f) => {
              await api("/admin/correos", "POST", fields(f));
              f.reset();
              mails.reload();
            }}
          >
            <h3>Añadir correo</h3>
            <Field name="email" title="Correo" type="email" required />
            <Field
              name="contrasena_actual"
              title="Contraseña actual"
              type="password"
              required
            />
            <button>Añadir correo</button>
          </Action>
        </section>
        <section className="panel">
          <h2>Cambiar contraseña</h2>
          <Action
            onSubmit={async (f) => {
              const d = fields(f);
              if (d.nueva_contrasena !== d.confirmar_contrasena)
                throw new Error("Las contraseñas no coinciden.");
              await api("/admin/contrasena", "PUT", d);
              setCsrf("");
              navigate("/admin");
            }}
          >
            <Field
              name="contrasena_actual"
              title="Contraseña actual"
              type="password"
              required
            />
            <Field
              name="nueva_contrasena"
              title="Nueva contraseña (mínimo 12 caracteres)"
              type="password"
              required
            />
            <Field
              name="confirmar_contrasena"
              title="Repite la nueva contraseña"
              type="password"
              required
            />
            <p className="muted">
              Al guardarla se cerrarán las sesiones abiertas.
            </p>
            <button>Guardar nueva contraseña</button>
          </Action>
        </section>
      </div>
    </AdminLayout>
  );
}
function Recovery({ verify = false }: { verify?: boolean }) {
  const [params] = useSearchParams(),
    token = params.get("token"),
    navigate = useNavigate();
  return (
    <main className="container narrow">
      <section className="panel">
        <h1>
          {verify
            ? "Verificar correo"
            : token
              ? "Nueva contraseña"
              : "Recuperar contraseña"}
        </h1>
        <Action
          success={
            verify
              ? "Correo verificado."
              : token
                ? "Contraseña actualizada. Ya puedes iniciar sesión."
                : "Si el correo está verificado, recibirás un enlace de recuperación."
          }
          onSubmit={async (f) => {
            const d = fields(f);
            if (verify)
              await api("/admin/correos/verificar", "POST", { token });
            else if (token) {
              if (d.nueva_contrasena !== d.confirmar_contrasena)
                throw new Error("Las contraseñas no coinciden.");
              await api("/admin/recuperacion/confirmar", "POST", {
                token,
                ...d,
              });
            } else await api("/admin/recuperacion/solicitar", "POST", d);
          }}
        >
          {verify ? (
            <p>Confirma la verificación de tu correo de recuperación.</p>
          ) : token ? (
            <>
              <Field
                name="nueva_contrasena"
                title="Nueva contraseña (mínimo 12 caracteres)"
                type="password"
                required
              />
              <Field
                name="confirmar_contrasena"
                title="Repite la nueva contraseña"
                type="password"
                required
              />
            </>
          ) : (
            <Field
              name="email"
              title="Correo de recuperación"
              type="email"
              required
            />
          )}
          <button disabled={verify && !token}>
            {verify
              ? "Verificar correo"
              : token
                ? "Guardar contraseña"
                : "Enviar enlace"}
          </button>
        </Action>
        <button className="text-button" onClick={() => navigate("/admin")}>
          Volver al acceso
        </button>
      </section>
    </main>
  );
}
function App() {
  const location = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);
  const [ids, setIds] = useState<string[]>(() => {
    try {
      const saved = JSON.parse(
        sessionStorage.getItem("licitex-comparar") || "[]",
      );
      return Array.isArray(saved)
        ? saved.filter((v) => typeof v === "string").slice(0, 100)
        : [];
    } catch {
      return [];
    }
  });
  useEffect(() => {
    sessionStorage.setItem("licitex-comparar", JSON.stringify(ids));
  }, [ids]);
  const toggle = (id: string) =>
    setIds((v) =>
      v.includes(id)
        ? v.filter((k) => k !== id)
        : v.length < 100
          ? [...v, id]
          : v,
    );
  return (
    <Selection.Provider value={{ ids, toggle }}>
      <header>
        <div className="container nav">
          <Link className="brand" to="/">
            <Compass size={27} />
            <span>
              Lici<span className="teal">tex</span>
              <small>ENCUENTRA TU EQUIPO</small>
            </span>
          </Link>
          <nav>
            <NavLink to="/">Inicio</NavLink>
            <NavLink to="/catalogo">Catálogo</NavLink>
            <NavLink to="/comparar">Comparador</NavLink>
            <NavLink to="/recomendador">Recomendador</NavLink>
          </nav>
          <Link className="admin-link" to="/admin">
            <LockKeyhole size={14} /> Admin
          </Link>
        </div>
      </header>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/catalogo" element={<Catalog />} />
        <Route path="/equipos/:id" element={<Detail />} />
        <Route path="/comparar" element={<Compare />} />
        <Route path="/recomendador" element={<Recommend />} />
        <Route path="/admin" element={<Login />} />
        <Route path="/admin/equipos" element={<AdminEquipment />} />
        <Route path="/admin/equipos/:id" element={<Editor />} />
        <Route path="/admin/reglas" element={<Rules />} />
        <Route path="/admin/cuenta" element={<Account />} />
        <Route path="/recuperar-contrasena" element={<Recovery />} />
        <Route path="/restablecer" element={<Recovery />} />
        <Route path="/restablecer-contrasena" element={<Recovery />} />
        <Route path="/verificar-correo" element={<Recovery verify />} />
        <Route
          path="*"
          element={
            <main className="container empty">
              <h1>Página no encontrada</h1>
              <Link to="/">Volver al inicio</Link>
            </main>
          }
        />
      </Routes>
      <footer>
        <div className="container">
          <div>
            <Link className="brand" to="/">
              Lici<span className="teal">tex</span>
            </Link>
            <p>Información para elegir. Herramientas para comparar.</p>
          </div>
          <span>GNSS hoy. Más posibilidades mañana.</span>
        </div>
      </footer>
      {ids.length > 0 && !location.pathname.startsWith("/admin") && (
        <aside className="compare-tray">
          <span>
            <Scale size={20} />
            {ids.length} seleccionados
          </span>
          <Link className="button" to="/comparar">
            Comparar <ArrowRight size={16} />
          </Link>
          <button
            className="icon"
            aria-label="Limpiar selección"
            onClick={() => setIds([])}
          >
            <X size={18} />
          </button>
        </aside>
      )}
    </Selection.Provider>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
