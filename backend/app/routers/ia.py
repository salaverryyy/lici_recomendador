from datetime import datetime, timedelta, timezone
import hashlib
import os
import re
from threading import Lock
from time import monotonic
import unicodedata

from fastapi import APIRouter, HTTPException, Request
from psycopg import Error as DatabaseError
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..cotecmi import es_cotecmi
from ..db import connect
from ..ia import AIProviderError, interpret, probe_status, status
from ..recomendador import Preferencias
from .controladoras import Requirements as ControllerRequirements, recommend as recommend_controller
from .recomendar import recomendar as recommend_gnss


router = APIRouter(prefix="/api/ia", tags=["asistente con IA"])
_rate_lock = Lock()
_rate_hits: dict[str, list[float]] = {}


def _limit(request: Request):
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client = forwarded or (request.client.host if request.client else "desconocido")
    maximum = max(1, int(os.getenv("AI_REQUESTS_PER_10_MINUTES", "10")))
    secret = os.getenv("AI_RATE_LIMIT_SECRET", os.getenv("ADMIN_SESSION_SECRET", "licitex-local"))
    client_hash = hashlib.sha256(f"{secret}:{client}".encode()).hexdigest()
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM ia_solicitudes WHERE creada_en < NOW() - INTERVAL '1 day'")
            cur.execute("SELECT COUNT(*) AS total FROM ia_solicitudes WHERE cliente_hash=%s AND creada_en >= NOW() - INTERVAL '10 minutes'", (client_hash,))
            if cur.fetchone()["total"] >= maximum:
                raise HTTPException(status_code=429, detail="Alcanzaste el límite temporal de consultas. Intenta nuevamente en unos minutos.")
            cur.execute("INSERT INTO ia_solicitudes(cliente_hash) VALUES(%s)", (client_hash,))
        return
    except HTTPException:
        raise
    except DatabaseError:
        pass  # Compatibilidad durante una migración: respaldo local del proceso.
    now = monotonic()
    with _rate_lock:
        recent = [instant for instant in _rate_hits.get(client, []) if now - instant < 600]
        if len(recent) >= maximum:
            raise HTTPException(
                status_code=429,
                detail="Alcanzaste el límite temporal de consultas. Intenta nuevamente en unos minutos.",
            )
        recent.append(now)
        _rate_hits[client] = recent


class PreviousContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo_equipo: str = Field(pattern=r"^(gnss|controladora)$")
    requisitos: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def limit_context(self):
        # El contexto lo envía el navegador: se limita para proteger la cuota
        # y evitar que se use como una segunda entrada sin restricciones.
        if len(self.requisitos) > 80 or len(str(self.requisitos)) > 20_000:
            raise ValueError("El contexto previo es demasiado grande.")
        return self


class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str = Field(pattern=r"^(user|assistant)$")
    text: str = Field(min_length=1, max_length=2500)


class AIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: str = Field(min_length=3, max_length=6000)
    tipo_equipo: str = Field(default="auto", pattern=r"^(auto|gnss|controladora)$")
    solo_cotecmi: bool = True
    top_n: int = Field(default=5, ge=1, le=10)
    contexto_previo: PreviousContext | None = None
    historial: list[ConversationMessage] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def limit_history(self):
        if sum(len(item.text) for item in self.historial) > 12_000:
            raise ValueError("El historial de conversación es demasiado grande.")
        return self


@router.get("/estado")
def ai_status(comprobar: bool = False):
    base = probe_status() if comprobar else status()
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT cuota_hasta,ultimo_codigo,motivo,actualizado_en FROM ia_estado_servicio WHERE id=TRUE")
            shared = cur.fetchone()
        if shared and shared["cuota_hasta"] and shared["cuota_hasta"] > datetime.now().astimezone():
            reason = shared["motivo"] or "cuota_agotada"
            message = ("La cuota gratuita de IA se agotó temporalmente." if reason == "cuota_agotada"
                       else "El proveedor de IA está temporalmente saturado. Licitex volverá a comprobarlo pronto.")
            return {"disponible": False, "motivo": reason, "codigo": shared["ultimo_codigo"] or 503,
                    "mensaje": message,
                    "reintentar_en": shared["cuota_hasta"].isoformat(), "comprobado_en": base.get("comprobado_en")}
    except Exception:
        pass
    return base


def _catalog(solo_cotecmi: bool, requested_type: str) -> list[dict]:
    """Contexto compacto, procedente exclusivamente de la base técnica auditada."""
    rows: list[dict] = []
    with connect() as conn, conn.cursor() as cur:
        if requested_type != "controladora":
            cur.execute("""
              SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.descripcion,e.anio_modelo,
                     e.pais_marca,e.pais_fabricacion,e.ficha_pdf_url,e.web_url,
                     to_jsonb(b) AS datos
              FROM equipos e LEFT JOIN base_evaluacion b USING(id_equipo)
              WHERE e.publicado AND e.categoria <> 'Controladora' ORDER BY e.marca,e.modelo
            """)
            allowed = {'canales_gnss','rtk_horizontal_mm','rtk_vertical_mm','rtk_ppm_h','rtk_ppm_v',
                       'red_rtk_horizontal_mm','red_rtk_vertical_mm','red_rtk_ppm_h','red_rtk_ppm_v',
                       'static_horizontal_mm','static_vertical_mm','static_ppm_h','static_ppm_v',
                       'largo_static_horizontal_mm','largo_static_vertical_mm','largo_static_ppm_h','largo_static_ppm_v',
                       'tiene_imu','inclinacion_imu_deg','tiene_camara','cantidad_camaras','laser',
                       'laser_alcance_m','autonomia_bateria','memoria','memoria_expandible',
                       'memoria_expandida_max_gb','lte_4g','uhf_tx_rx_integrada','proteccion_ip',
                       'radio_frecuencia','radio_potencia_max_w','cantidad_baterias','lemo','lemo_pines',
                       'peso_max','temperatura_operacion_min_c','temperatura_operacion_max_c',
                       'gps','glonass','galileo','beidou','qzss','navic_irnss','sbas',
                       'tiene_ppp','ppp_h_cm','ppp_v_cm','bluetooth','wifi','usb','usb_c','rs232',
                       'auditoria_fuente','auditoria_notas','tecnica_fuente','tecnica_notas'}
            for row in cur.fetchall():
                data = row.pop('datos') or {}
                rows.append({**row, **{key: data.get(key) for key in allowed}})
        if requested_type != "gnss":
            cur.execute("""
              SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.descripcion,e.anio_modelo,
                     e.pais_marca,e.pais_fabricacion,e.ficha_pdf_url,e.web_url,
                     to_jsonb(c) AS datos
              FROM equipos e LEFT JOIN controladora_especificaciones c USING(id_equipo)
              WHERE e.publicado AND e.categoria='Controladora' ORDER BY e.marca,e.modelo
            """)
            allowed = {'sistema_operativo','android_version','ram_gb','almacenamiento_gb','expansion_gb',
                       'pantalla_pulgadas','teclado_qwerty','autonomia_h','lte_4g','proteccion_ip','caida_m','fuente'}
            for row in cur.fetchall():
                data = row.pop('datos') or {}
                rows.append({**row, **{key: data.get(key) for key in allowed}})
    selected = [dict(row) for row in rows if not solo_cotecmi or es_cotecmi(row["marca"])]
    return [{key: value for key, value in row.items() if value is not None and value != ""} for row in selected]


_RAG_STOPWORDS = {
    "ademas", "ahora", "algo", "cual", "cuales", "como", "con", "del", "desde",
    "donde", "el", "ella", "ese", "esta", "este", "estos", "hay", "las", "los",
    "mas", "me", "mejor", "para", "pero", "por", "que", "quiero", "sin", "son",
    "sus", "tiene", "una", "uno", "unos", "usar", "y",
}


def _search_text(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(value).casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _retrieve_catalog(rows: list[dict], query: str, limit: int | None = None) -> list[dict]:
    """RAG léxico local: recupera fichas relevantes sin embeddings ni otra cuota."""
    maximum = limit or max(3, min(20, int(os.getenv("AI_RAG_MAX_EQUIPMENT", "12"))))
    normalized_query = _search_text(query)
    terms = {
        token for token in re.findall(r"[a-z0-9][a-z0-9+.-]{1,}", normalized_query)
        if len(token) >= 3 and token not in _RAG_STOPWORDS
    }
    scored: list[tuple[float, dict]] = []
    for row in rows:
        model = _search_text(row.get("modelo", ""))
        brand = _search_text(row.get("marca", ""))
        haystack = _search_text(" ".join(f"{key} {value}" for key, value in row.items()))
        score = min(len(row), 50) / 1000
        if model and model in normalized_query:
            score += 12
        if brand and brand in normalized_query:
            score += 6
        score += sum(2 if term in model else 1 for term in terms if term in haystack)
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1].get("marca", ""), item[1].get("modelo", "")))
    return [row for _, row in scored[:maximum]]


def _mark_shared_error(exc: AIProviderError):
    if not (exc.quota or exc.retryable):
        return
    if exc.retry_at is None:
        exc.retry_at = datetime.now(timezone.utc) + timedelta(minutes=2)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("UPDATE ia_estado_servicio SET cuota_hasta=%s,ultimo_codigo=%s,motivo=%s,actualizado_en=NOW() WHERE id=TRUE",
                        (exc.retry_at, exc.code or 429, exc.reason))
    except Exception:
        pass


def _answer(kind: str, ranking: dict, omitted: list[str]) -> str:
    results = ranking.get("resultados", [])
    if not results:
        return "No encontré equipos publicados para evaluar con esos requisitos."
    first = results[0]
    equipment = first["equipo"]
    percent = first.get("porcentaje")
    intro = f"La mejor coincidencia es {equipment['marca']} {equipment['modelo']}"
    if percent is not None:
        intro += f", con {percent}% de ajuste a los requisitos evaluados"
    intro += "."
    if kind == "gnss":
        detail = first.get("explicacion", "")
    else:
        met = [d["nombre"] for d in first.get("detalle", []) if d["estado"] == "cumple"]
        failed = [d["nombre"] for d in first.get("detalle", []) if d["estado"] == "no_cumple"]
        unknown = [d["nombre"] for d in first.get("detalle", []) if d["estado"] == "sin_datos"]
        parts = []
        if met:
            parts.append("Cumple: " + ", ".join(met) + ".")
        if failed:
            parts.append("No cumple: " + ", ".join(failed) + ".")
        if unknown:
            parts.append("Sin información: " + ", ".join(unknown) + ".")
        detail = " ".join(parts)
    closing = " Revisa la ficha técnica y las condiciones de la oferta antes de decidir."
    if omitted:
        closing = " Algunos requisitos no pudieron evaluarse automáticamente. " + closing.strip()
    return " ".join(part for part in (intro, detail, closing) if part)


@router.post("/recomendar")
def ai_recommend(body: AIRequest, request: Request):
    _limit(request)
    previous = body.contexto_previo
    try:
        full_catalog = _catalog(body.solo_cotecmi, body.tipo_equipo)
        history = [item.model_dump() for item in body.historial]
        retrieval_query = "\n".join(
            [*(item["text"] for item in history), body.mensaje,
             str(previous.requisitos) if previous else ""]
        )
        catalog = _retrieve_catalog(full_catalog, retrieval_query)
        parsed = interpret(
            body.mensaje,
            body.tipo_equipo,
            previous.tipo_equipo if previous else None,
            previous.requisitos if previous else None,
            catalog,
            history,
        )
    except AIProviderError as exc:
        _mark_shared_error(exc)
        return {"estado": "no_disponible", "motivo": exc.reason, "codigo": exc.code or 503,
                "reintentable": exc.retryable or exc.quota, "mensaje": str(exc),
                "reintentar_en": exc.retry_at.isoformat() if exc.retry_at else None}
    except DatabaseError:
        return {"estado": "no_disponible", "motivo": "catalogo", "codigo": 503,
                "reintentable": True,
                "mensaje": "No se pudo consultar el catálogo técnico en este momento.",
                "reintentar_en": None}

    ranking = None
    if parsed["tiene_criterios"]:
        if parsed["tipo_equipo"] == "gnss":
            ranking = recommend_gnss(
                Preferencias(
                    **parsed["requisitos"], solo_cotecmi=body.solo_cotecmi, top_n=body.top_n
                )
            )
        else:
            ranking = recommend_controller(
                ControllerRequirements(
                    requisitos=parsed["requisitos"],
                    solo_cotecmi=body.solo_cotecmi,
                    top_n=body.top_n,
                )
            )

    return {
        "estado": "ok",
        **parsed,
        "solo_cotecmi": body.solo_cotecmi,
        "ranking": ranking,
        "memoria": {
            "turnos_usados": len(body.historial) // 2,
            "mensajes_usados": len(body.historial),
            "equipos_recuperados": [item["id_equipo"] for item in catalog],
            "persistencia": "navegador",
        },
        "respuesta": _answer(parsed["tipo_equipo"], ranking, parsed["omitidos"])
        if ranking else (parsed["respuesta_general"] or "Puedo orientarte con el catálogo disponible. Cuéntame el tipo de trabajo o las condiciones que más te importan."),
        "generado_en": datetime.now().astimezone().isoformat(),
    }
