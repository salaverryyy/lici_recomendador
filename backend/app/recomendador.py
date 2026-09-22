from dataclasses import dataclass
import re

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Preferencias(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    solo_cotecmi: bool = False
    top_n: int = Field(default=3, ge=1, le=100)
    cantidad_baterias_min: int | None = Field(default=None, ge=1, le=20)
    baterias_incluidas_por_receptor_min: int | None = Field(default=None, ge=1, le=20)
    inclinacion_imu_min_deg: float | None = Field(default=None, ge=0, le=180)
    actualizacion_min_hz: float | None = Field(default=None, ge=0)
    usb: bool | None = None
    usb_c: bool | None = None
    rs232: bool | None = None
    red_rtk_horizontal_max_mm: float | None = Field(default=None, ge=0)
    red_rtk_vertical_max_mm: float | None = Field(default=None, ge=0)
    red_rtk_ppm_h_max: float | None = Field(default=None, ge=0)
    red_rtk_ppm_v_max: float | None = Field(default=None, ge=0)
    necesita_lemo: bool | None = None
    lemo_pines: int | None = Field(default=None, ge=1, le=30)
    rtk_modo: str = Field(default='linea_base', pattern=r'^(linea_base|red)$')
    static_modo: str = Field(default='rapido', pattern=r'^(rapido|largo)$')
    necesita_imu: bool | None = None
    imu_generacion: str | None = Field(default=None, min_length=1, max_length=100)
    gps: bool | None = None
    glonass: bool | None = None
    galileo: bool | None = None
    beidou: bool | None = None
    qzss: bool | None = None
    navic_irnss: bool | None = None
    sbas: bool | None = None
    bluetooth: bool | None = None
    wifi: bool | None = None
    uhf_tx_rx_integrada: bool | None = None
    lte_4g: bool | None = None
    radio_potencia_ajustable: bool | None = None
    radio_potencia_min_w: float | None = Field(default=None, ge=0)
    protocolo_multimarca: bool | None = None
    bateria_interna: bool | None = None
    registro_rinex_3: bool | None = None
    registro_propietario: bool | None = None
    necesita_camara: bool | None = None
    cantidad_camaras_min: int | None = Field(default=None, ge=1, le=20)
    necesita_snlonglink: bool | None = None
    canales_min: int | None = Field(default=None, ge=0)
    rtk_ppm_max: float | None = Field(default=None, ge=0)
    static_ppm_max: float | None = Field(default=None, ge=0)
    rtk_ppm_h_max: float | None = Field(default=None, ge=0)
    rtk_ppm_v_max: float | None = Field(default=None, ge=0)
    static_ppm_h_max: float | None = Field(default=None, ge=0)
    static_ppm_v_max: float | None = Field(default=None, ge=0)
    rtk_horizontal_max_mm: float | None = Field(default=None, ge=0)
    rtk_vertical_max_mm: float | None = Field(default=None, ge=0)
    static_horizontal_max_mm: float | None = Field(default=None, ge=0)
    static_vertical_max_mm: float | None = Field(default=None, ge=0)
    radio_min_mhz: float | None = Field(default=None, ge=0)
    radio_max_mhz: float | None = Field(default=None, ge=0)
    constelaciones_min: int | None = Field(default=None, ge=1, le=6)
    autonomia_min_h: float | None = Field(default=None, ge=0)
    memoria_min_gb: float | None = Field(default=None, ge=0)
    sim_4g: bool | None = None
    laser: bool | None = None
    laser_alcance_min_m: float | None = Field(default=None, ge=0)
    bateria_intercambiable: bool | None = None
    bateria_caliente: bool | None = None
    camara_mp_min: float | None = Field(default=None, ge=0)
    peso_max_g: int | None = Field(default=None, ge=0)
    largo_max_mm: float | None = Field(default=None, ge=0)
    ancho_max_mm: float | None = Field(default=None, ge=0)
    alto_max_mm: float | None = Field(default=None, ge=0)
    tiempo_inicializacion_max_s: int | None = Field(default=None, ge=0)
    temperatura_operacion_min_c: float | None = Field(default=None, ge=-273.15, le=200)
    temperatura_operacion_max_c: float | None = Field(default=None, ge=-273.15, le=200)
    temperatura_almacenamiento_min_c: float | None = Field(default=None, ge=-273.15, le=200)
    temperatura_almacenamiento_max_c: float | None = Field(default=None, ge=-273.15, le=200)
    humedad_min_pct: float | None = Field(default=None, ge=0, le=100)
    humedad_condicion: str | None = Field(default=None, pattern=r"^(Sin condensación|Con condensación)$")
    caida_min_m: float | None = Field(default=None, ge=0)
    proteccion_ip_aceptada: str | None = Field(default=None, pattern=r"^IP[0-6][0-9](?:,IP[0-6][0-9])*$", max_length=120)
    vibracion_norma: str | None = Field(default=None, pattern=r"^MIL-STD-810[FGH]$")

    @model_validator(mode="after")
    def validar_radio(self):
        for grupo in ("operacion", "almacenamiento"):
            minimo = getattr(self, f"temperatura_{grupo}_min_c")
            maximo = getattr(self, f"temperatura_{grupo}_max_c")
            if minimo is not None and maximo is not None and minimo > maximo:
                raise ValueError("La temperatura mínima solicitada supera la máxima.")
        if self.rtk_modo == 'red' and any(getattr(self, k) is not None for k in
            ('red_rtk_horizontal_max_mm','red_rtk_vertical_max_mm','red_rtk_ppm_h_max','red_rtk_ppm_v_max')):
            raise ValueError('Para exigir línea base y red simultáneamente, selecciona Línea base y completa los campos adicionales RTK en red.')
        # Compatibilidad con clientes anteriores que enviaban un único umbral ppm.
        for grupo in ("rtk", "static"):
            conjunto = getattr(self, grupo + "_ppm_max")
            if conjunto is not None:
                for eje in ("h", "v"):
                    campo = grupo + "_ppm_" + eje + "_max"
                    individual = getattr(self, campo)
                    if individual is not None and individual != conjunto:
                        raise ValueError("No combines umbrales ppm generales e individuales distintos.")
                    setattr(self, campo, conjunto)
        if (self.radio_min_mhz is None) != (self.radio_max_mhz is None):
            raise ValueError("Indica ambos extremos del rango de radio, o deja ambos vacíos.")
        if self.radio_min_mhz is not None and self.radio_min_mhz > self.radio_max_mhz:
            raise ValueError("La frecuencia mínima no puede superar la máxima.")
        return self


@dataclass(frozen=True)
class Criterio:
    clave: str
    campo_input: str
    campo_equipo: str | None
    nombre: str
    unidad: str | None
    modo: str
    peso: float


CRITERIOS = (
    Criterio('baterias_incluidas_por_receptor','baterias_incluidas_por_receptor_min','baterias_incluidas_por_receptor','Baterías incluidas por receptor',None,'minimo',3),
    Criterio('inclinacion_imu_deg','inclinacion_imu_min_deg','inclinacion_imu_deg','Inclinación IMU admitida','°','minimo',4),
    Criterio('actualizacion_hz','actualizacion_min_hz','actualizacion_hz','Salida de posición GNSS','Hz','minimo',3),
    *(Criterio(k,k,k,n,None,'booleano',2) for k,n in [('usb','USB'),('usb_c','USB-C'),('rs232','RS-232')]),
    Criterio('red_rtk_horizontal_mm','red_rtk_horizontal_max_mm','red_rtk_horizontal_mm','RTK en red horizontal','mm','maximo',6),
    Criterio('red_rtk_vertical_mm','red_rtk_vertical_max_mm','red_rtk_vertical_mm','RTK en red vertical','mm','maximo',6),
    Criterio('red_rtk_ppm_h','red_rtk_ppm_h_max','red_rtk_ppm_h','RTK en red horizontal','ppm','maximo',2),
    Criterio('red_rtk_ppm_v','red_rtk_ppm_v_max','red_rtk_ppm_v','RTK en red vertical','ppm','maximo',2),
    Criterio('cantidad_baterias','cantidad_baterias_min','cantidad_baterias','Cantidad de baterías del equipo',None,'minimo',3),
    Criterio('lemo','necesita_lemo','lemo','Conector LEMO',None,'booleano',3),
    Criterio('lemo_pines','lemo_pines','lemo_pines','Pines del conector LEMO',None,'exacto',3),
    *(Criterio(campo, campo, campo, nombre, None, "booleano", 1)
      for campo, nombre in (("gps", "GPS"), ("glonass", "GLONASS"), ("galileo", "Galileo"),
                            ("beidou", "BeiDou"), ("qzss", "QZSS"), ("navic_irnss", "NavIC/IRNSS"), ("sbas", "SBAS"))),
    Criterio("imu_generacion", "imu_generacion", "imu_generacion", "Generación de IMU declarada", None, "generacion", 3),
    *(Criterio(campo, campo, campo, nombre, None, "booleano", 3)
      for campo, nombre in (("bluetooth", "Bluetooth"), ("wifi", "Wi-Fi"),
                            ("uhf_tx_rx_integrada", "Radio UHF integrada Tx/Rx"), ("lte_4g", "4G LTE integrado"),
                            ("radio_potencia_ajustable", "Potencia de radio ajustable"),
                            ("protocolo_multimarca", "Protocolos de radio para múltiples marcas"),
                            ("bateria_interna", "Batería interna"), ("registro_rinex_3", "Registro RINEX 3.x"),
                            ("registro_propietario", "Registro en formato propietario"))),
    Criterio("radio_potencia_max_w", "radio_potencia_min_w", "radio_potencia_max_w", "Potencia de transmisión disponible", "W", "minimo", 3),
    Criterio("temperatura_operacion_min_c", "temperatura_operacion_min_c", "temperatura_operacion_min_c", "Frío de operación requerido", "°C", "ambiente_min", 4),
    Criterio("temperatura_operacion_max_c", "temperatura_operacion_max_c", "temperatura_operacion_max_c", "Calor de operación requerido", "°C", "ambiente_max", 4),
    Criterio("temperatura_almacenamiento_min_c", "temperatura_almacenamiento_min_c", "temperatura_almacenamiento_min_c", "Frío de almacenamiento requerido", "°C", "ambiente_min", 2),
    Criterio("temperatura_almacenamiento_max_c", "temperatura_almacenamiento_max_c", "temperatura_almacenamiento_max_c", "Calor de almacenamiento requerido", "°C", "ambiente_max", 2),
    Criterio("humedad_max_pct", "humedad_min_pct", "humedad_max_pct", "Humedad soportada", "%", "minimo", 3),
    Criterio("humedad_condicion", "humedad_condicion", "humedad_condicion", "Condición de humedad", None, "texto_exacto", 2),
    Criterio("caida_m", "caida_min_m", "caida_m", "Caída ensayada", "m", "minimo", 3),
    Criterio("proteccion_ip", "proteccion_ip_aceptada", "proteccion_ip", "Protección IP aceptada", None, "ip", 5),
    Criterio("vibracion_norma", "vibracion_norma", "vibracion_norma", "Norma de ensayo de vibración", None, "norma", 3),
    Criterio("tiene_imu", "necesita_imu", "tiene_imu", "IMU", None, "booleano", 10),
    Criterio("tiene_camara", "necesita_camara", "tiene_camara", "Cámara", None, "booleano", 8),
    Criterio("cantidad_camaras", "cantidad_camaras_min", "cantidad_camaras", "Cantidad de cámaras", None, "minimo", 6),
    Criterio("tiene_snlonglink", "necesita_snlonglink", "tiene_snlonglink", "SNLongLink", None, "booleano", 5),
    Criterio("canales_gnss", "canales_min", "canales_gnss", "Canales GNSS", None, "minimo", 5),
    Criterio("rtk_ppm_h", "rtk_ppm_h_max", "rtk_ppm_h", "RTK horizontal", "ppm", "maximo", 2),
    Criterio("rtk_ppm_v", "rtk_ppm_v_max", "rtk_ppm_v", "RTK vertical", "ppm", "maximo", 2),
    Criterio("static_ppm_h", "static_ppm_h_max", "static_ppm_h", "Estático horizontal", "ppm", "maximo", 2),
    Criterio("static_ppm_v", "static_ppm_v_max", "static_ppm_v", "Estático vertical", "ppm", "maximo", 2),
    Criterio("rtk_horizontal_mm", "rtk_horizontal_max_mm", "rtk_horizontal_mm", "RTK horizontal", "mm", "maximo", 6),
    Criterio("rtk_vertical_mm", "rtk_vertical_max_mm", "rtk_vertical_mm", "RTK vertical", "mm", "maximo", 6),
    Criterio("static_horizontal_mm", "static_horizontal_max_mm", "static_horizontal_mm", "Estático horizontal", "mm", "maximo", 6),
    Criterio("static_vertical_mm", "static_vertical_max_mm", "static_vertical_mm", "Estático vertical", "mm", "maximo", 6),
    Criterio("radio_rango", "radio_min_mhz", None, "Radio compatible", "MHz", "radio", 5),
    Criterio("constelaciones", "constelaciones_min", "constelaciones", "Constelaciones", None, "minimo", 4),
    Criterio("autonomia_bateria", "autonomia_min_h", "autonomia_bateria", "Autonomía", "h", "minimo", 5),
    Criterio("memoria", "memoria_min_gb", "memoria", "Memoria", "GB", "minimo", 3),
    Criterio("sim_4g", "sim_4g", "sim_4g", "SIM 4G", None, "booleano", 5),
    Criterio("laser", "laser", "laser", "Láser", None, "booleano", 8),
    Criterio("laser_alcance_m", "laser_alcance_min_m", "laser_alcance_m", "Alcance del láser", "m", "minimo", 5),
    Criterio("bateria_intercambiable", "bateria_intercambiable", "bateria_intercambiable", "Batería intercambiable", None, "booleano", 4),
    Criterio("bateria_caliente", "bateria_caliente", "bateria_caliente", "Batería en caliente", None, "booleano", 4),
    Criterio("mp_camara", "camara_mp_min", "mp_camara", "Cámara", "MP", "minimo", 3),
    Criterio("peso_max", "peso_max_g", "peso_max", "Peso", "g", "maximo", 3),
    Criterio("dimensiones", "largo_max_mm", None, "Dimensiones", "mm", "dimensiones", 1),
    Criterio("tiempo_inicializacion", "tiempo_inicializacion_max_s", "tiempo_inicializacion", "Inicialización RTK", "s", "maximo", 2),
)

CRITERIOS_POR_CLAVE = {criterio.clave: criterio for criterio in CRITERIOS}


def criterios_seleccionados(preferencias: Preferencias):
    elegidos = []
    for criterio in CRITERIOS:
        valor = getattr(preferencias, criterio.campo_input)
        if criterio.modo == "dimensiones":
            activo = any(getattr(preferencias, campo) is not None for campo in ("largo_max_mm", "ancho_max_mm", "alto_max_mm"))
        elif criterio.modo == "booleano":
            activo = valor is True
        else:
            activo = valor is not None
        if activo:
            elegidos.append(criterio)
    return elegidos


def evaluar_equipo(preferencias, criterios, pesos, evaluacion, rangos):
    datos = evaluacion or {}
    detalle = []
    for criterio in criterios:
        pedido = getattr(preferencias, criterio.campo_input)
        valor = datos.get(criterio.campo_equipo) if criterio.campo_equipo else None
        estado = "sin_datos"
        factor = 0.0
        observacion = None
        if criterio.clave in ('rtk_horizontal_mm','rtk_vertical_mm','rtk_ppm_h','rtk_ppm_v'):
            modo = 'RTK en red' if preferencias.rtk_modo == 'red' else 'RTK de línea base / RTK declarado'
            if preferencias.rtk_modo == 'red': valor = datos.get('red_'+criterio.clave)
            observacion = modo
        elif criterio.clave in ('static_horizontal_mm','static_vertical_mm','static_ppm_h','static_ppm_v'):
            modo = 'Estático de observaciones largas' if preferencias.static_modo == 'largo' else 'Estático / estático rápido'
            if preferencias.static_modo == 'largo': valor = datos.get('largo_'+criterio.clave)
            observacion = modo
        memoria_fabrica = None
        requiere_ampliacion = False

        # Los límites térmicos se evalúan por cumplimiento, sin dividir valores
        # Celsius negativos. Si se necesita cámara, aplicar su rango restringido.
        if criterio.modo in ("ambiente_min", "ambiente_max"):
            if criterio.clave.startswith("temperatura_operacion_") and (
                preferencias.necesita_camara is True or (preferencias.cantidad_camaras_min or 0) > 0
            ):
                eje = "min" if criterio.modo == "ambiente_min" else "max"
                camara = datos.get(f"temperatura_camara_{eje}_c")
                if camara is not None:
                    valor = camara if valor is None else (max(valor, camara) if eje == "min" else min(valor, camara))
            if valor is not None:
                cumple = valor <= pedido if criterio.modo == "ambiente_min" else valor >= pedido
                estado = "cumple" if cumple else "incumple"
                factor = float(cumple)
        elif criterio.modo in ("ip", "texto_exacto", "norma", "generacion", "exacto"):
            if valor is not None:
                if criterio.modo == "ip":
                    declarados = set(re.findall(r"IP[0-6][0-9]", valor))
                    cumple = bool(declarados.intersection(pedido.split(",")))
                elif criterio.modo == "norma":
                    # Versión explícita; no inferir equivalencia entre revisiones.
                    declaradas = {"MIL-STD-810" + version for version in re.findall(r"MIL[- ]STD[- ]810([FGH])", valor.upper())}
                    cumple = pedido in declaradas
                else:
                    cumple = valor == pedido
                estado = "cumple" if cumple else "incumple"
                factor = float(cumple)

        elif criterio.modo == "booleano":
            if valor is not None:
                estado = "cumple" if valor is True else "incumple"
                factor = 1.0 if estado == "cumple" else 0.0
        elif criterio.modo in ("minimo", "maximo"):
            if criterio.clave == "memoria":
                memoria_fabrica = valor
                ampliada = datos.get("memoria_expandida_max_gb")
                if datos.get("memoria_expandible") is True and ampliada is not None and (valor is None or ampliada > valor):
                    if valor is None or valor < pedido:
                        valor = ampliada
                        requiere_ampliacion = True
                        observacion = f"Memoria de fábrica: {memoria_fabrica if memoria_fabrica is not None else 'sin datos'} GB; capacidad ampliada declarada: {ampliada} GB."
            if valor is not None:
                estado = "cumple" if (
                    valor >= pedido if criterio.modo == "minimo" else valor <= pedido
                ) else "incumple"
                if estado == "cumple":
                    factor = 1.0
                    if requiere_ampliacion:
                        observacion = "Cumple con memoria extendida. " + observacion
                elif criterio.modo == "minimo":
                    factor = float(valor) / float(pedido) if pedido else 0.0
                else:
                    factor = float(pedido) / float(valor) if valor else 0.0
            elif criterio.clave == "mp_camara" and datos.get("tiene_camara") is False:
                estado = "incumple"
        elif criterio.modo == "radio":
            pedido = {"min_mhz": preferencias.radio_min_mhz, "max_mhz": preferencias.radio_max_mhz}
            valor = rangos
            if rangos:
                estado = "cumple" if any(
                    rango["min_mhz"] <= preferencias.radio_min_mhz
                    and rango["max_mhz"] >= preferencias.radio_max_mhz
                    for rango in rangos
                ) else "incumple"
                factor = 1.0 if estado == "cumple" else 0.0
        elif criterio.modo == "dimensiones":
            pedido = {
                campo: getattr(preferencias, campo)
                for campo in ("largo_max_mm", "ancho_max_mm", "alto_max_mm")
                if getattr(preferencias, campo) is not None
            }
            nombres = {"largo_max_mm": "largo_mm", "ancho_max_mm": "ancho_mm", "alto_max_mm": "alto_mm"}
            valor = {campo: datos.get(nombres[campo]) for campo in pedido}
            if all(actual is not None for actual in valor.values()):
                estado = "cumple" if all(valor[campo] <= maximo for campo, maximo in pedido.items()) else "incumple"
                factor = sum(
                    1.0 if valor[campo] <= maximo else float(maximo) / float(valor[campo])
                    for campo, maximo in pedido.items()
                ) / len(pedido)

        factor = max(0.0, min(1.0, factor))
        peso = pesos[criterio.clave]
        detalle.append({
            "clave": criterio.clave,
            "nombre": criterio.nombre,
            "unidad": criterio.unidad,
            "pedido": pedido,
            "valor_equipo": valor,
            "estado": estado,
            "observacion": observacion,
            "requiere_ampliacion": requiere_ampliacion,
            "memoria_fabrica_gb": memoria_fabrica if criterio.clave == "memoria" else None,
            "factor": round(factor, 4),
            "peso": peso,
            "puntos": round(peso * factor, 4),
        })

    peso_total = sum(item["peso"] for item in detalle)
    puntos = sum(item["puntos"] for item in detalle)
    porcentaje = round(100 * puntos / peso_total, 2) if peso_total else None
    cumplidos = [item["nombre"] + (" ("+item['unidad']+")" if item['unidad'] else '') + (" (con memoria extendida)" if item["requiere_ampliacion"] else "")
                 for item in detalle if item["estado"] == "cumple"]
    incumplidos = [item["nombre"] + (" ("+item['unidad']+")" if item['unidad'] else '') for item in detalle if item["estado"] == "incumple"]
    desconocidos = [item["nombre"] + (" ("+item['unidad']+")" if item['unidad'] else '') for item in detalle if item["estado"] == "sin_datos"]
    partes = []
    if cumplidos:
        partes.append("Cumple: " + ", ".join(cumplidos) + ".")
    if incumplidos:
        partes.append("No cumple: " + ", ".join(incumplidos) + ".")
    if desconocidos:
        partes.append("Sin datos: " + ", ".join(desconocidos) + ".")
    return {
        "porcentaje": porcentaje,
        "puntos": puntos,
        "peso_total": peso_total,
        "cumplimientos": len(cumplidos),
        "incumplimientos": len(incumplidos),
        "sin_datos": len(desconocidos),
        "detalle": detalle,
        "explicacion": " ".join(partes),
    }
