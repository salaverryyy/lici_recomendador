import { useEffect, useState } from "react";
import { api } from "./api";

export function SoftwareCard({
  software,
  evaluation,
}: {
  software: any;
  evaluation?: any;
}) {
  // Metadatos legibles locales; no consume IA ni realiza consultas por tarjeta.
  const names: Record<string, string> = {
    estatico: "Estático",
    cinematico: "Cinemático / PPK",
    ajuste_red: "Ajuste de redes",
    rinex: "Importación RINEX",
    rinex_2: "RINEX 2.x",
    rinex_3: "RINEX 3.x",
    informes: "Informes",
    geotag: "Geotag de imágenes",
    gratuito: "Gratuito",
    windows: "Windows",
    macos: "macOS",
    exporta_dxf: "DXF",
    exporta_csv: "CSV",
  };
  return (
    <article className="panel software-card">
      <span className="eyebrow">{software.marca} · SOFTWARE DE OFICINA</span>
      <h3>{software.nombre}</h3>
      <p>{software.descripcion}</p>
      {evaluation?.porcentaje != null && (
        <p>
          <strong>{evaluation.porcentaje}%</strong> de los requisitos de
          software evaluados; no acredita el conjunto.
        </p>
      )}
      {!!evaluation?.detalle?.length && (
        <ul>
          {evaluation.detalle.map((d: any) => (
            <li key={d.clave}>
              {d.nombre}:{" "}
              <strong>
                {d.estado === "cumple"
                  ? "Cumple"
                  : d.estado === "sin_datos"
                    ? "Pendiente de confirmar"
                    : "No cumple"}
              </strong>
            </li>
          ))}
        </ul>
      )}
      <details>
        <summary>Funciones, formatos, licencia y fuentes</summary>
        <dl className="software-specs">
          {Object.entries(names)
            .filter(([key]) => key in (software.funciones || {}))
            .map(([key, name]) => (
              <div key={key}>
                <dt>{name}</dt>
                <dd
                  className={
                    software.funciones[key] == null ? "software-unknown" : ""
                  }
                >
                  {software.funciones[key] === true
                    ? "Sí"
                    : software.funciones[key] === false
                      ? "No"
                      : "Pendiente de confirmar"}
                </dd>
              </div>
            ))}
        </dl>
        <p>{software.formatos}</p>
        <p>
          <strong>Licencia:</strong> {software.licencia}
        </p>
        <p>{software.compatibilidad}</p>
        <ul>
          {software.fuentes.map((f: any) => (
            <li key={f.url}>
              <a href={f.url} target="_blank" rel="noopener noreferrer">
                {f.url.includes("kpn.com.uy")
                  ? "Manual del fabricante · copia del distribuidor"
                  : "Fuente del fabricante"}{" "}
                ↗
              </a>{" "}
              · {f.fecha_consulta}
              <p className="small-text">{f.alcance}</p>
            </li>
          ))}
        </ul>
      </details>
    </article>
  );
}

export function SoftwareCatalog() {
  const [data, setData] = useState<any>(null),
    [error, setError] = useState(""),
    [query, setQuery] = useState("");
  useEffect(() => {
    let active = true;
    api("/software")
      .then((v) => active && setData(v))
      .catch((e) => active && setError(e.message));
    return () => {
      active = false;
    };
  }, []);
  const rows = (data?.software || []).filter((s: any) =>
    (s.marca + " " + s.nombre + " " + s.descripcion)
      .toLocaleLowerCase()
      .includes(query.toLocaleLowerCase()),
  );
  return (
    <main className="container">
      <div className="page-title">
        <div>
          <span className="eyebrow">GNSS → CONTROLADORA → SOFTWARE</span>
          <h1>Software de procesamiento</h1>
          <p>
            Programas de oficina con funciones y fuentes verificadas. Distintos
            del software de campo de la controladora.
          </p>
        </div>
      </div>
      <label>
        Buscar por nombre o marca
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="PProcessing, Compass Solution, Emlid Studio…"
        />
      </label>
      {error && (
        <p role="alert" className="notice error">
          {error}
        </p>
      )}
      {!data && !error && <p role="status">Cargando software…</p>}
      <div className="grid">
        {rows.map((s: any) => (
          <SoftwareCard key={s.id_software} software={s} />
        ))}
      </div>
      {data && !rows.length && (
        <p>No hay programas que coincidan con la búsqueda.</p>
      )}
    </main>
  );
}
