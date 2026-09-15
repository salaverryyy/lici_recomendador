from fastapi import APIRouter, HTTPException, Query
from psycopg import Error as DatabaseError

from ..db import connect


router = APIRouter(prefix="/api", tags=["comparador"])

COLUMNAS = {
    "marca": ("Marca", None),
    "modelo": ("Modelo", None),
    "categoria": ("Categoría", None),
    "anio_modelo": ("Año del modelo", None),
    "tiene_imu": ("IMU", None),
    "tiene_camara": ("Cámara", None),
    "canales_gnss": ("Canales GNSS", None),
    "memoria": ("Memoria", "GB"),
    "sim_4g": ("SIM 4G", None),
    "laser": ("Láser", None),
    "bateria_intercambiable": ("Batería intercambiable", None),
    "bateria_caliente": ("Batería en caliente", None),
    "mp_camara": ("Cámara", "MP"),
    "radio_frecuencia": ("Radio (texto técnico)", None),
    "radio_rangos": ("Rangos de radio", "MHz"),
    "constelaciones": ("Constelaciones", None),
    "autonomia_bateria": ("Autonomía", "h"),
    "peso_max": ("Peso", "g"),
    "tiempo_inicializacion": ("Tiempo de encendido", "s"),
    "rtk_horizontal_mm": ("RTK horizontal", "mm"),
    "rtk_vertical_mm": ("RTK vertical", "mm"),
    "rtk_ppm_h": ("RTK horizontal", "ppm"),
    "rtk_ppm_v": ("RTK vertical", "ppm"),
    "static_horizontal_mm": ("Estático horizontal", "mm"),
    "static_vertical_mm": ("Estático vertical", "mm"),
    "static_ppm_h": ("Estático horizontal", "ppm"),
    "static_ppm_v": ("Estático vertical", "ppm"),
    "largo_mm": ("Largo", "mm"),
    "ancho_mm": ("Ancho", "mm"),
    "alto_mm": ("Alto", "mm"),
    "gps": ("GPS", None),
    "glonass": ("GLONASS", None),
    "galileo": ("Galileo", None),
    "beidou": ("BeiDou", None),
    "qzss": ("QZSS", None),
    "navic_irnss": ("NavIC/IRNSS", None),
    "sbas": ("SBAS", None),
    "tiene_ppp": ("PPP", None),
    "ppp_h_cm": ("PPP horizontal", "cm"),
    "ppp_v_cm": ("PPP vertical", "cm"),
}

COLUMNAS_PREDETERMINADAS = [
    "tiene_imu", "tiene_camara", "canales_gnss", "constelaciones",
    "rtk_horizontal_mm", "rtk_vertical_mm", "autonomia_bateria",
    "peso_max", "radio_rangos",
]


@router.get("/comparar/columnas")
def columnas_disponibles():
    return [
        {"clave": clave, "nombre": nombre, "unidad": unidad}
        for clave, (nombre, unidad) in COLUMNAS.items()
    ]


@router.get("/comparar")
def comparar(
    ids: str = Query(description="IDs separados por coma; mínimo 2"),
    columnas: str | None = Query(default=None, description="Claves separadas por coma; omitir para columnas predeterminadas"),
):
    equipos_ids = [valor.strip() for valor in ids.split(",") if valor.strip()]
    if not 2 <= len(equipos_ids) <= 100 or len(set(equipos_ids)) != len(equipos_ids):
        raise HTTPException(status_code=422, detail="Elige entre 2 y 100 equipos distintos.")

    claves = (
        [valor.strip() for valor in columnas.split(",") if valor.strip()]
        if columnas is not None else COLUMNAS_PREDETERMINADAS
    )
    if not claves or len(set(claves)) != len(claves) or any(c not in COLUMNAS for c in claves):
        raise HTTPException(status_code=422, detail="Selecciona columnas válidas y sin repetir.")

    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.*, to_jsonb(b) AS evaluacion
                FROM equipos AS e
                LEFT JOIN base_evaluacion AS b USING (id_equipo)
                WHERE e.publicado = TRUE AND e.id_equipo = ANY(%s)
                """,
                (equipos_ids,),
            )
            encontrados = {fila["id_equipo"]: fila for fila in cur.fetchall()}
            faltantes = [valor for valor in equipos_ids if valor not in encontrados]
            if faltantes:
                raise HTTPException(status_code=404, detail={"equipos_no_encontrados": faltantes})

            cur.execute(
                """
                SELECT id_equipo, frecuencia_min_mhz, frecuencia_max_mhz
                FROM equipo_radio_frecuencia
                WHERE id_equipo = ANY(%s)
                ORDER BY frecuencia_min_mhz, frecuencia_max_mhz
                """,
                (equipos_ids,),
            )
            rangos = {valor: [] for valor in equipos_ids}
            for fila in cur.fetchall():
                rangos[fila["id_equipo"]].append({
                    "min_mhz": fila["frecuencia_min_mhz"],
                    "max_mhz": fila["frecuencia_max_mhz"],
                })

            return {
                "equipos": [
                    {"id_equipo": valor, "marca": encontrados[valor]["marca"], "modelo": encontrados[valor]["modelo"]}
                    for valor in equipos_ids
                ],
                "columnas": [
                    {
                        "clave": clave,
                        "nombre": COLUMNAS[clave][0],
                        "unidad": COLUMNAS[clave][1],
                        "valores": {
                            valor: (
                                rangos[valor] if clave == "radio_rangos"
                                else encontrados[valor].get(clave, (encontrados[valor]["evaluacion"] or {}).get(clave))
                            )
                            for valor in equipos_ids
                        },
                    }
                    for clave in claves
                ],
            }
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar el catálogo en PostgreSQL.") from exc
