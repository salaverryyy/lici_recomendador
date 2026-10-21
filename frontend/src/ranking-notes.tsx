export const ORDER_NOTE =
  "En igualdad técnica: preferencia comercial SinoGNSS, luego menor precio orientativo comparable y año más reciente. Las referencias no son precios Cotecmi ni costos finales en Perú. Este orden no concede puntos ni acredita superioridad técnica.";

export function complianceLabel(detail: any) {
  if (detail.estado !== "cumple")
    return detail.estado === "sin_datos" ? "Sin datos" : "No cumple";
  if (detail.requiere_adaptador)
    return "Cumple con adaptador LEMO–USB-C de carga y datos";
  if (!detail.requiere_ampliacion) return "Cumple";
  if (detail.opcion_interna)
    return "Cumple con memoria interna de fábrica bajo pedido";
  return detail.tipo_ampliacion === "opcion_fabrica"
    ? "Cumple con configuración opcional de fábrica"
    : "Cumple con ampliación";
}

export function ExpansionNotice({ details }: { details?: any[] }) {
  const conditional =
    details?.filter(
      (d) =>
        d.estado === "cumple" &&
        (d.requiere_ampliacion || d.requiere_adaptador),
    ) || [];
  if (!conditional.length) return null;
  return (
    <div className="notice">
      {conditional.map((d) => (
        <p key={d.clave}>
          <strong>
            {d.nombre}: {complianceLabel(d)}.
          </strong>{" "}
          {d.requiere_adaptador ? (
            d.observacion
          ) : (
            <>
              Capacidad estándar:{" "}
              {d.memoria_fabrica_gb == null
                ? "sin confirmar"
                : `${d.memoria_fabrica_gb} GB`}
              ; capacidad evaluada: {d.valor_equipo} {d.unidad}. La ampliación o
              configuración debe incluirse y verificarse en la oferta.
            </>
          )}
        </p>
      ))}
    </div>
  );
}

export function ModelYear({ equipment }: { equipment: any }) {
  return (
    <p className="muted small-text">
      {equipment.anio_modelo
        ? `Año del modelo: ${equipment.anio_modelo}`
        : "Año del modelo sin confirmar"}
    </p>
  );
}

export function PriceReference({ equipment }: { equipment: any }) {
  const price = equipment.referencia_precio;
  if (!price?.precio_usd && !price?.precio_origen)
    return (
      <p className="muted small-text">
        Costo orientativo: cotizar; sin precio público comparable.
      </p>
    );
  return (
    <details className="small-text">
      <summary>
        Referencia:{" "}
        {price.precio_usd
          ? `US$ ${Number(price.precio_usd).toLocaleString("en-US", { minimumFractionDigits: 2 })}`
          : `${price.moneda_origen} ${Number(price.precio_origen).toLocaleString()}`}{" "}
        · no es cotización Cotecmi
      </summary>
      <p>{price.alcance}</p>
      <a href={price.fuente_url} target="_blank" rel="noopener noreferrer">
        Fuente comercial
      </a>{" "}
      · {price.fecha_consulta}
    </details>
  );
}
