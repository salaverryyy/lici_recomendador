from fastapi import APIRouter, HTTPException, Query
from psycopg import Error as DatabaseError

from ..db import connect
from ..controladoras import META


router = APIRouter(prefix="/api", tags=["comparador"])

COLUMNAS = {
    "imu_generacion": ("Generación de IMU declarada", None),
    "imu_tecnologia": ("Tecnología de IMU", None),
    "memoria_expandible": ("Memoria ampliable", None),
    "memoria_expandida_max_gb": ("Capacidad con ampliación declarada", "GB"),
    "memoria_opcional_fabrica_max_gb": ("Capacidad opcional de fábrica", "GB"),
    "bluetooth": ("Bluetooth", None),
    "bluetooth_version": ("Versión Bluetooth", None),
    "wifi": ("Wi-Fi", None),
    "wifi_estandar": ("Estándar Wi-Fi", None),
    "uhf_tx_rx_integrada": ("UHF integrada Tx/Rx", None),
    "uhf_modo": ("Modos de radio integrada", None),
    "lte_4g": ("4G LTE integrado", None),
    "radio_potencia_ajustable": ("Potencia de radio ajustable", None),
    "radio_potencia_max_w": ("Potencia máxima de transmisión", "W"),
    "protocolo_multimarca": ("Protocolos de radio para múltiples marcas", None),
    "radio_protocolos": ("Protocolos de radio declarados", None),
    "bateria_interna": ("Batería interna", None),
    "tipo_bateria": ("Tipo de batería", None),
    "registro_rinex": ("Registro RINEX", None),
    "registro_rinex_3": ("Registro RINEX 3.x", None),
    "rinex_versiones": ("Versiones RINEX declaradas", None),
    "registro_propietario": ("Registro en formato propietario", None),
    "formato_propietario": ("Formato propietario de registro", None),
    "tecnica_notas": ("Condiciones de las especificaciones", None),
    "tecnica_fuente": ("Fuente de especificaciones", None),
    'temperatura_operacion_min_c': ('Temperatura mínima de operación', '°C'),
    'temperatura_operacion_max_c': ('Temperatura máxima de operación', '°C'),
    'temperatura_almacenamiento_min_c': ('Temperatura mínima de almacenamiento', '°C'),
    'temperatura_almacenamiento_max_c': ('Temperatura máxima de almacenamiento', '°C'),
    'temperatura_camara_min_c': ('Temperatura mínima con cámara', '°C'),
    'temperatura_camara_max_c': ('Temperatura máxima con cámara', '°C'),
    'humedad_max_pct': ('Humedad máxima', '%'),
    'caida_m': ('Altura de caída ensayada', 'm'),
    'humedad_condicion': ('Condición de humedad', None),
    'proteccion_ip': ('Protección IP declarada', None),
    'caida_condiciones': ('Condiciones del ensayo de caída', None),
    'vibracion_norma': ('Ensayo de vibración', None),
    'choque_condiciones': ('Choque funcional', None),
    'ambiental_notas': ('Notas ambientales', None),
    'ambiental_fuente': ('Fuente ambiental', None),

    "marca": ("Marca", None),
    "modelo": ("Modelo", None),
    "categoria": ("Categoría", None),
    "anio_modelo": ("Año del modelo", None),
    "tiene_imu": ("IMU", None),
    "tiene_camara": ("Cámara", None),
    "cantidad_camaras": ("Cantidad de cámaras", None),
    "tiene_snlonglink": ("SNLongLink", None),
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
    "peso_max", "radio_rangos", "laser", "cantidad_camaras", "memoria", "tiene_snlonglink",
]


@router.get("/comparar/columnas")
def columnas_disponibles():
    return [
        {"clave": clave, "nombre": nombre, "unidad": unidad}
        for clave, (nombre, unidad) in COLUMNAS.items()
    ] + [{'clave':'controladora_'+k,'nombre':v['nombre']+' · Controladora','unidad':v['unidad']} for k,v in META.items()]


@router.get("/comparar")
def comparar(
    ids: str = Query(description="IDs separados por coma; mínimo 1"),
    columnas: str | None = Query(default=None, description="Claves separadas por coma; omitir para columnas predeterminadas"),
):
    equipos_ids = [valor.strip() for valor in ids.split(",") if valor.strip()]
    if not 1 <= len(equipos_ids) <= 100 or len(set(equipos_ids)) != len(equipos_ids):
        raise HTTPException(status_code=422, detail="Elige entre 1 y 100 equipos distintos.")

    claves = (
        [valor.strip() for valor in columnas.split(",") if valor.strip()]
        if columnas is not None else COLUMNAS_PREDETERMINADAS
    )
    disponibles = {**COLUMNAS, **{'controladora_'+k:(v['nombre'],v['unidad']) for k,v in META.items()}}
    if not claves or len(set(claves)) != len(claves) or any(c not in disponibles for c in claves):
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

            controllers = [ident for ident in equipos_ids if encontrados[ident]['categoria']=='Controladora']
            if controllers:
                cur.execute('SELECT * FROM controladora_especificaciones WHERE id_equipo=ANY(%s)',(controllers,))
                for row in cur.fetchall():
                    encontrados[row['id_equipo']].update({'controladora_'+k:v for k,v in row.items() if k in META})
            if len(controllers)==len(equipos_ids) and not any(k.startswith('controladora_') for k in claves):
                claves=['marca','modelo']+['controladora_'+k for k in META]

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
                        "nombre": disponibles[clave][0],
                        "unidad": disponibles[clave][1],
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
