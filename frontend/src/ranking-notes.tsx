export const ORDER_NOTE =
  "En igualdad técnica se prioriza SinoGNSS; dentro de la marca, el menor costo de mercado comparable disponible y después el año más reciente. Los costos son internos; la falta de referencia no demuestra que un equipo sea más caro. Este orden no concede puntos ni acredita superioridad técnica.";

export function complianceLabel(detail: any) {
  if (detail.estado !== "cumple")
    return detail.estado === "sin_datos" ? "Sin datos" : "No cumple";
  if (detail.requiere_adaptador)
    return "Cumple transferencia de archivos con adaptador LEMO–USB-C, sin carga";
  if (detail.requiere_enlace_compartido)
    return "Cumple mediante enlace 4G/LTE compartido";
  if (detail.requiere_conversion)
    return `Cumple mediante conversión con ${detail.software_conversion || "software documentado"}`;
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
        (d.requiere_ampliacion ||
          d.requiere_adaptador ||
          d.requiere_enlace_compartido ||
          d.requiere_conversion),
    ) || [];
  if (!conditional.length) return null;
  return (
    <div className="notice">
      {conditional.map((d) => (
        <p key={d.clave}>
          <strong>
            {d.nombre}: {complianceLabel(d)}.
          </strong>{" "}
          {d.requiere_adaptador ||
          d.requiere_enlace_compartido ||
          d.requiere_conversion ? (
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
