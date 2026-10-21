export const ORDER_NOTE =
  "En igualdad técnica: año de modelo más reciente primero; a igual año, preferencia comercial SinoGNSS. Los años sin confirmar van al final. Este orden no concede puntos ni acredita superioridad técnica.";

export function complianceLabel(detail: any) {
  if (detail.estado !== "cumple")
    return detail.estado === "sin_datos" ? "Sin datos" : "No cumple";
  if (!detail.requiere_ampliacion) return "Cumple";
  return detail.tipo_ampliacion === "opcion_fabrica"
    ? "Cumple con configuración opcional de fábrica"
    : "Cumple con ampliación";
}

export function ExpansionNotice({ details }: { details?: any[] }) {
  const conditional =
    details?.filter((d) => d.estado === "cumple" && d.requiere_ampliacion) ||
    [];
  if (!conditional.length) return null;
  return (
    <div className="notice">
      {conditional.map((d) => (
        <p key={d.clave}>
          <strong>
            {d.nombre}: {complianceLabel(d)}.
          </strong>{" "}
          Capacidad estándar:{" "}
          {d.memoria_fabrica_gb == null
            ? "sin confirmar"
            : `${d.memoria_fabrica_gb} GB`}
          ; capacidad evaluada: {d.valor_equipo} {d.unidad}. La ampliación o
          configuración debe incluirse y verificarse en la oferta.
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
