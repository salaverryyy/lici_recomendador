from datetime import datetime, timedelta, timezone
import os
import re
import unicodedata

from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..cotecmi import es_cotecmi
from ..db import connect
from ..ia import AIProviderError, interpret, probe_status, status
from ..recomendador import Preferencias
from .controladoras import Requirements as ControllerRequirements, recommend as recommend_controller
from .recomendar import recomendar as recommend_gnss
from .recomendar import limitar_con_empates
from .slam import Requirements as SlamRequirements, recommend as recommend_slam
from .software import catalogo as software_catalog
from ..software import rank as recommend_software, comparison_advice
from ..soluciones import assemble, unscored


router = APIRouter(prefix="/api/ia", tags=["asistente con IA"])


class PreviousContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo_equipo: str = Field(pattern=r"^(gnss|controladora|slam|software|kit)$")
    requisitos: dict = Field(default_factory=dict)
    componentes: dict = Field(default_factory=dict)
    selecciones: dict[str, str] = Field(default_factory=dict)
    referencia_gnss: str | None = Field(default=None, max_length=100)
    misma_marca: bool = False

    @model_validator(mode="after")
    def limit_context(self):
        # El contexto lo envía el navegador: se limita para proteger la cuota
        # y evitar que se use como una segunda entrada sin restricciones.
        if len(self.requisitos) > 80 or len(str(self.requisitos)) > 20_000:
            raise ValueError("El contexto previo es demasiado grande.")
        if set(self.componentes)-{'gnss','controladora','software'} or set(self.selecciones)-{'gnss','controladora','software'} or len(str(self.componentes))>20_000 or any(not isinstance(v,dict) or len(v)>80 for v in self.componentes.values()) or any(len(v)>100 for v in self.selecciones.values()):
            raise ValueError('Contexto de conjunto inválido.')
        return self


class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str = Field(pattern=r"^(user|assistant)$")
    text: str = Field(min_length=1, max_length=2500)


class AIRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: str = Field(min_length=3, max_length=6000)
    tipo_equipo: str = Field(default="auto", pattern=r"^(auto|gnss|controladora|slam|software|kit)$")
    solo_cotecmi: bool = True
    top_n: int = Field(default=20, ge=1, le=100)
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
        if requested_type in ("auto", "gnss"):
            cur.execute("""
              SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.descripcion,e.anio_modelo,
                     e.pais_marca,e.pais_fabricacion,e.ficha_pdf_url,e.web_url,
                     to_jsonb(b) AS datos
              FROM equipos e LEFT JOIN base_evaluacion b USING(id_equipo)
              WHERE e.publicado AND e.categoria='GNSS' ORDER BY e.marca,e.modelo
            """)
            allowed = {'canales_gnss','rtk_horizontal_mm','rtk_vertical_mm','rtk_ppm_h','rtk_ppm_v',
                       'red_rtk_horizontal_mm','red_rtk_vertical_mm','red_rtk_ppm_h','red_rtk_ppm_v',
                       'static_horizontal_mm','static_vertical_mm','static_ppm_h','static_ppm_v',
                       'largo_static_horizontal_mm','largo_static_vertical_mm','largo_static_ppm_h','largo_static_ppm_v',
                       'tiene_imu','inclinacion_imu_deg','tiene_camara','cantidad_camaras','laser',
                       'laser_alcance_m','autonomia_bateria','memoria','memoria_expandible','memoria_es_interna',
                       'memoria_expandida_max_gb','memoria_opcional_fabrica_max_gb','lte_4g','uhf_tx_rx_integrada','proteccion_ip',
                       'radio_frecuencia','radio_potencia_max_w','cantidad_baterias','lemo','lemo_pines',
                       'peso_max','temperatura_operacion_min_c','temperatura_operacion_max_c',
                       'gps','glonass','galileo','beidou','qzss','navic_irnss','sbas',
                       'tiene_ppp','ppp_h_cm','ppp_v_cm','bluetooth','wifi','usb','usb_c','rs232',
                       'auditoria_fuente','auditoria_notas','tecnica_fuente','tecnica_notas'}
            for row in cur.fetchall():
                data = row.pop('datos') or {}
                rows.append({**row, **{key: data.get(key) for key in allowed}})
        if requested_type in ('auto','software','kit'):
            cur.execute("SELECT id_software AS id_equipo,marca,nombre AS modelo,'Software de procesamiento' AS categoria,descripcion,funciones,licencia,formatos,compatibilidad,fuentes FROM software_procesamiento WHERE publicado ORDER BY marca,nombre")
            rows.extend(cur.fetchall())
        if requested_type in ("auto", "controladora"):
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
        if requested_type in ("auto", "slam"):
            cur.execute("""
              SELECT e.id_equipo,e.marca,e.modelo,e.categoria,e.descripcion,e.anio_modelo,
                     e.pais_marca,e.pais_fabricacion,e.ficha_pdf_url,e.web_url,
                     to_jsonb(s) AS datos
              FROM equipos e LEFT JOIN slam_especificaciones s USING(id_equipo)
              WHERE e.publicado AND e.categoria='Escáner SLAM' ORDER BY e.marca,e.modelo
            """)
            allowed = {
                'aplicaciones','tecnologia_slam','lineas_lidar','laser_clase_1',
                'alcance_lidar_m','puntos_por_segundo','fov_horizontal_deg','fov_vertical_deg',
                'precision_nube_cm','gnss_disponible','gnss_integrado','gnss_opcional',
                'rtk_disponible','operacion_sin_gnss','tiene_imu','cantidad_camaras',
                'resolucion_camara_mp','colorizacion_rgb','visualizacion_tiempo_real',
                'peso_operativo_g','autonomia_h','baterias_incluidas','hot_swap',
                'proteccion_ip','temperatura_operacion_min_c','temperatura_operacion_max_c',
                'almacenamiento_gb','almacenamiento_expandible','usb_c','wifi','bluetooth',
                'software_adquisicion_incluido','software_postproceso_incluido',
                'exporta_las','exporta_laz','exporta_e57','exporta_ply','exporta_dxf',
                'formatos_salida','modos_montaje','software','notas','fuente',
            }
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


def _explicit_catalog_type(rows: list[dict], query: str) -> str | None:
    """Permite cambiar de familia cuando el usuario nombra un modelo inequívoco."""
    normalized = _search_text(query)
    category_types = {
        "GNSS": "gnss",
        "Controladora": "controladora",
        "Escáner SLAM": "slam",
        "Software de procesamiento": "software",
    }
    matches = set()
    for row in rows:
        model = _search_text(row.get("modelo", "")).strip()
        if not model or (len(model) < 3 and not any(char.isdigit() for char in model)):
            continue
        if re.search(rf"(?<![a-z0-9]){re.escape(model)}(?![a-z0-9])", normalized):
            kind = category_types.get(row.get("categoria"))
            if kind:
                matches.add(kind)
    return next(iter(matches)) if len(matches) == 1 else None


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
    lead = "Una de las mejores coincidencias es" if ranking.get("empate_en_primer_puesto") else "La mejor coincidencia es"
    intro = f"{lead} {equipment['marca']} {equipment['modelo']}"
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
        closing = (
            f" Hay {len(omitted)} requisitos pendientes de revisión manual: este porcentaje "
            "no acredita el cumplimiento total de la licitación. " + closing.strip()
        )
    return " ".join(part for part in (intro, detail, closing) if part)


@router.post("/recomendar")
def ai_recommend(body: AIRequest):
    previous = body.contexto_previo
    try:
        full_catalog = _catalog(body.solo_cotecmi, "auto")
        requested_type = body.tipo_equipo
        eligible_catalog = full_catalog
        history = [item.model_dump() for item in body.historial]
        retrieval_query = "\n".join(
            [*(item["text"] for item in history), body.mensaje,
             str(previous.requisitos) if previous else ""]
        )
        # Cada familia conserva espacio: los receptores no desplazan todo el software/colectoras.
        catalog = []
        for category in ('GNSS','Controladora','Software de procesamiento','Escáner SLAM'):
            catalog.extend(_retrieve_catalog([r for r in eligible_catalog if r.get('categoria')==category], retrieval_query, limit=8 if category=='GNSS' else 4))
        preserved = ({*previous.selecciones.values(), previous.referencia_gnss} if previous else set())
        catalog.extend(r for r in full_catalog if r['id_equipo'] in preserved and r not in catalog)
        parsed = interpret(
            body.mensaje,
            requested_type,
            previous.tipo_equipo if previous else None,
            previous.requisitos if previous else None,
            catalog,
            history,
            previous.model_dump() if previous else None,
        )
    except AIProviderError as exc:
        _mark_shared_error(exc)
        return {"estado": "no_disponible", "motivo": exc.reason, "codigo": exc.code or 503,
                "reintentable": exc.retryable or exc.quota or exc.reason in ("respuesta_invalida", "respuesta_truncada"), "mensaje": str(exc),
                "reintentar_en": exc.retry_at.isoformat() if exc.retry_at else None}
    except DatabaseError:
        return {"estado": "no_disponible", "motivo": "catalogo", "codigo": 503,
                "reintentable": True,
                "mensaje": "No se pudo consultar el catálogo técnico en este momento.",
                "reintentar_en": None}

    if parsed['tipo_equipo'] != 'slam':
        try:
            workflow = _recommend_workflow(parsed, body, full_catalog)
        except (DatabaseError, HTTPException) as exc:
            return {'estado':'no_disponible','motivo':'catalogo','codigo':503,'reintentable':True,'mensaje':'No se pudo calcular el conjunto con el catálogo. Intenta nuevamente.'}
        except ValueError as exc:
            return {'estado':'no_disponible','motivo':'seleccion_invalida','codigo':422,'reintentable':True,'mensaje':str(exc)}
        return {'estado':'ok', **parsed, **workflow, 'solo_cotecmi':body.solo_cotecmi,
                'memoria':{'mensajes_usados':len(body.historial),'turnos_usados':len(body.historial)//2,
                           'equipos_recuperados':[r['id_equipo'] for r in catalog],'persistencia':'navegador'},
                'generado_en':datetime.now().astimezone().isoformat()}

    ranking = None
    if parsed["tiene_criterios"]:
        if parsed["tipo_equipo"] == "gnss":
            ranking = recommend_gnss(
                Preferencias(
                    **parsed["requisitos"], solo_cotecmi=body.solo_cotecmi, top_n=body.top_n
                )
            )
        elif parsed["tipo_equipo"] == "controladora":
            ranking = recommend_controller(
                ControllerRequirements(
                    requisitos=parsed["requisitos"],
                    solo_cotecmi=body.solo_cotecmi,
                    top_n=body.top_n,
                )
            )
        else:
            ranking = recommend_slam(
                SlamRequirements(
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


def _recommend_workflow(parsed, body, catalog):
    components = parsed['componentes']
    selected = parsed['selecciones']
    categories = {'gnss':'GNSS','controladora':'Controladora','software':'Software de procesamiento'}
    for family, ident in selected.items():
        if not any(r['id_equipo']==ident and r['categoria']==categories[family] for r in catalog):
            raise ValueError('La selección no está publicada o no pertenece al catálogo permitido. Vuelve a elegir el modelo.')
    previous = body.contexto_previo
    # El filtro Cotecmi se aplica de nuevo a cada turno, incluso a IDs enviados por el navegador.
    reference = previous.referencia_gnss if previous and not components.get('gnss') and parsed['tipo_equipo']!='gnss' else None
    if previous and parsed['tipo_equipo'] in ('controladora','software'):
        reference = previous.referencia_gnss
    if reference and not any(r['id_equipo']==reference and r['categoria']=='GNSS' for r in catalog):
        reference = None
    ranks = {}
    for family in ('gnss','controladora'):
        requirements = components.get(family, {})
        if requirements:
            ranks[family] = recommend_gnss(Preferencias(**requirements, solo_cotecmi=body.solo_cotecmi, top_n=100)) if family=='gnss' else recommend_controller(ControllerRequirements(requisitos=requirements,solo_cotecmi=body.solo_cotecmi,top_n=100))
        else:
            ranks[family] = {'resultados':[unscored(r) for r in catalog if r['categoria']==categories[family]]}
    software = software_catalog(body.solo_cotecmi)
    gnss_results = ranks['gnss']['resultados']
    anchor = selected.get('gnss') or reference
    if not anchor and components.get('gnss') and gnss_results:
        anchor = gnss_results[0]['equipo']['id_equipo']
    brand = next((r['marca'] for r in catalog if r['id_equipo']==anchor), None)
    ranks['software'] = recommend_software(software, components.get('software', {}), brand, parsed['misma_marca'])
    # Sin requisitos/selección GNSS no se inventa un receptor ganador.
    # Recordar requisitos de otras familias no autoriza mostrar un kit en cada turno.
    kind = parsed['tipo_equipo']
    show_solution = kind == 'kit' or (kind in ('software','controladora') and (selected.get('gnss') or reference))
    eligible_gnss = gnss_results if show_solution and (components.get('gnss') or selected.get('gnss') or reference) else []
    solution = assemble(eligible_gnss, ranks['controladora']['resultados'], software, components, selected,
                        reference, parsed['misma_marca'], body.top_n)
    kind = parsed['tipo_equipo']
    ranking = ranks.get(kind) if kind in ('gnss','controladora') and components.get(kind) else None
    if ranking and 'mostrados' in ranking:
        ranking = {**ranking, 'resultados':limitar_con_empates(ranking['resultados'],body.top_n)}
        ranking['mostrados'] = len(ranking['resultados'])
    usb_list = kind == 'gnss' and components.get('gnss') == {'usb_c': True} and re.search(r'lista|todos|cu[aá]les', body.mensaje, re.I)
    if usb_list and ranking:
        matches = [r for r in ranks['gnss']['resultados'] if any(d.get('clave') == 'usb_c' and d['estado'] == 'cumple' for d in r.get('detalle', []))]
        ranking = {**ranking, 'resultados':matches, 'mostrados':len(matches)}
    if solution['opciones']:
        first = solution['opciones'][0]
        names = [first['gnss']['equipo']['marca']+' '+first['gnss']['equipo']['modelo'],
                 first['controladora']['equipo']['modelo'] if first['controladora'] else (first.get('app_campo') or {}).get('nombre','controladora pendiente'),
                 first['software']['software']['nombre'] if first['software'] else 'software pendiente']
        answer = 'Propuesta en orden GNSS → controladora → software de oficina: **'+' → '.join(names)+'**. '
        answer += ('El conjunto tiene incumplimientos documentados. ' if first['estado']=='no_cumple' else '')
        answer += 'Es una propuesta parcial: verifica cada bloque, compatibilidad, archivos y licencias; no acredita cumplimiento total.'
    elif kind=='software':
        answer = comparison_advice(body.mensaje, software, components.get('software', {}), brand) or parsed['respuesta_general'] or 'Estos son los softwares de oficina auditados. Elige el GNSS para asociar el programa de su marca y revisar el conjunto.'
    else:
        answer = _answer(kind, ranking, parsed['omitidos']) if ranking else parsed['respuesta_general'] or 'Indica el receptor o sus requisitos para construir el conjunto GNSS, controladora y software.'
    if usb_list and ranking:
        answer = f"Hay **{len(ranking['resultados'])} modelos con USB-C confirmado** en el catálogo permitido. Se listan solo los confirmados; los equipos sin datos o sin ese puerto quedan fuera. Tener USB-C no acredita carga ni una modalidad de transferencia concreta."
    if solution['opciones'] and not selected.get('gnss'):
        answer += ' El GNSS mostrado es una referencia provisional; puedes elegir otra opción.'
    if kind == 'software' and solution['opciones']:
        advice = comparison_advice(body.mensaje, software, components.get('software', {}), brand)
        if advice:
            answer += ' ' + advice
    reference = selected.get('gnss') or (solution['opciones'][0]['gnss']['equipo']['id_equipo'] if solution['opciones'] else reference)
    return {'ranking':ranking,'rankings':ranks,'solucion':solution,'respuesta':answer,
            'contexto':{'tipo_equipo':kind,'requisitos':parsed['requisitos'],'componentes':components,
                        'selecciones':selected,'misma_marca':parsed['misma_marca'],'referencia_gnss':reference}}
