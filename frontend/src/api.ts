// El frontend y la API comparten origen mediante proxy; la cookie HttpOnly no se lee en JavaScript.
let csrf = "";
export const setCsrf = (value: string) => {
  csrf = value;
};
export async function api(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<any> {
  const headers: Record<string, string> = {};
  if (body !== undefined && !(body instanceof FormData))
    headers["Content-Type"] = "application/json";
  if (method !== "GET" && csrf) headers["X-CSRF-Token"] = csrf;
  let response: Response;
  try {
    response = await fetch("/api" + path, {
      method,
      credentials: "same-origin",
      headers,
      body:
        body === undefined
          ? undefined
          : body instanceof FormData
            ? body
            : JSON.stringify(body),
    });
  } catch {
    throw new Error(
      "No se pudo conectar. Comprueba que el backend está encendido.",
    );
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) {
      csrf = "";
      window.dispatchEvent(new Event("sesion-expirada"));
    }
    const detail = data.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail
              .map(
                (e: any) => `${e.loc?.slice(1).join(".") || "Campo"}: ${e.msg}`,
              )
              .join(" · ")
          : "No se pudo completar la operación. Revisa los campos seleccionados.",
    );
  }
  return data;
}
