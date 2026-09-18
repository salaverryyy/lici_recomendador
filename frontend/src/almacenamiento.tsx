import { useEffect, useState } from "react";
import { api } from "./api";

export async function uploadFile(base: string, tipo: string, archivo: File) {
  const max = (tipo === "foto" ? 5 : 20) * 1024 * 1024;
  if (!archivo.size || archivo.size > max)
    throw new Error(
      `El archivo debe contener datos y no superar ${tipo === "foto" ? 5 : 20} MB.`,
    );
  const inicio = await api(base + "/archivos/iniciar", "POST", {
    tipo,
    bytes: archivo.size,
  });
  try {
    let numero = 0;
    for (
      let offset = 0;
      offset < archivo.size;
      offset += inicio.fragmento_bytes
    ) {
      await api(
        `/admin/archivos/fragmento/${numero++}?token=${encodeURIComponent(inicio.token)}`,
        "PUT",
        archivo.slice(offset, offset + inicio.fragmento_bytes),
      );
    }
    await api("/admin/archivos/finalizar", "POST", { token: inicio.token });
  } catch (e) {
    await api("/admin/archivos/cancelar", "POST", {
      token: inicio.token,
    }).catch(() => {});
    throw e;
  } finally {
    window.dispatchEvent(new Event("almacenamiento-actualizado"));
  }
}

export function StorageUsage() {
  const [data, setData] = useState<any>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function reload() {
    setBusy(true);
    setError("");
    try {
      setData(await api("/admin/almacenamiento"));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  useEffect(() => {
    void reload();
    window.addEventListener("almacenamiento-actualizado", reload);
    return () =>
      window.removeEventListener("almacenamiento-actualizado", reload);
  }, []);
  return (
    <section className="panel">
      <h3>Espacio de almacenamiento</h3>
      {data && (
        <>
          <p>
            {(data.bytes / 1e9).toFixed(3)} GB ocupados · {data.archivos}{" "}
            archivos · referencia: 10 GB
          </p>
          <progress
            max={data.referencia_bytes}
            value={Math.min(data.bytes, data.referencia_bytes)}
          />
          <p className="muted">
            {data.proveedor === "s3"
              ? "Tamaño actual de este bucket de R2. Los 10 GB son la franquicia gratuita mensual, compartida con otros buckets de la cuenta; no representan la facturación acumulada."
              : "Archivos locales de desarrollo; no representan el uso de R2."}
          </p>
        </>
      )}
      {error && <p role="alert">{error}</p>}
      <button
        type="button"
        className="outline small"
        disabled={busy}
        onClick={reload}
      >
        {busy ? "Consultando…" : "Actualizar espacio"}
      </button>
    </section>
  );
}
