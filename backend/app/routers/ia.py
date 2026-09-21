from datetime import datetime
import os
from threading import Lock
from time import monotonic

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..ia import AIProviderError, interpret, status
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


class AIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: str = Field(min_length=3, max_length=6000)
    tipo_equipo: str = Field(default="auto", pattern=r"^(auto|gnss|controladora)$")
    solo_cotecmi: bool = False
    top_n: int = Field(default=5, ge=1, le=10)
    contexto_previo: PreviousContext | None = None


@router.get("/estado")
def ai_status():
    return status()


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
        parsed = interpret(
            body.mensaje,
            body.tipo_equipo,
            previous.tipo_equipo if previous else None,
            previous.requisitos if previous else None,
        )
    except AIProviderError as exc:
        if exc.quota:
            return {
                "estado": "no_disponible",
                "motivo": "cuota_agotada",
                "mensaje": str(exc),
                "reintentar_en": exc.retry_at.isoformat() if exc.retry_at else None,
            }
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
        "respuesta": _answer(parsed["tipo_equipo"], ranking, parsed["omitidos"])
        if ranking
        else "Necesito al menos un requisito técnico concreto para calcular el ranking.",
        "generado_en": datetime.now().astimezone().isoformat(),
    }
