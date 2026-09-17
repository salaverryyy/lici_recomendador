from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Preferencias(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    top_n: int = Field(default=3, ge=1, le=100)
    necesita_imu: bool | None = None
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
    bateria_intercambiable: bool | None = None
    bateria_caliente: bool | None = None
    camara_mp_min: float | None = Field(default=None, ge=0)
    peso_max_g: int | None = Field(default=None, ge=0)
    largo_max_mm: float | None = Field(default=None, ge=0)
    ancho_max_mm: float | None = Field(default=None, ge=0)
    alto_max_mm: float | None = Field(default=None, ge=0)
    tiempo_inicializacion_max_s: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_radio(self):
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
    Criterio("bateria_intercambiable", "bateria_intercambiable", "bateria_intercambiable", "Batería intercambiable", None, "booleano", 4),
    Criterio("bateria_caliente", "bateria_caliente", "bateria_caliente", "Batería en caliente", None, "booleano", 4),
    Criterio("mp_camara", "camara_mp_min", "mp_camara", "Cámara", "MP", "minimo", 3),
    Criterio("peso_max", "peso_max_g", "peso_max", "Peso", "g", "maximo", 3),
    Criterio("dimensiones", "largo_max_mm", None, "Dimensiones", "mm", "dimensiones", 1),
    Criterio("tiempo_inicializacion", "tiempo_inicializacion_max_s", "tiempo_inicializacion", "Encendido", "s", "maximo", 2),
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

        if criterio.modo == "booleano":
            if valor is not None:
                estado = "cumple" if valor is True else "incumple"
                factor = 1.0 if estado == "cumple" else 0.0
        elif criterio.modo in ("minimo", "maximo"):
            if valor is not None:
                estado = "cumple" if (
                    valor >= pedido if criterio.modo == "minimo" else valor <= pedido
                ) else "incumple"
                if estado == "cumple":
                    factor = 1.0
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
            "factor": round(factor, 4),
            "peso": peso,
            "puntos": round(peso * factor, 4),
        })

    peso_total = sum(item["peso"] for item in detalle)
    puntos = sum(item["puntos"] for item in detalle)
    porcentaje = round(100 * puntos / peso_total, 2) if peso_total else None
    cumplidos = [item["nombre"] for item in detalle if item["estado"] == "cumple"]
    incumplidos = [item["nombre"] for item in detalle if item["estado"] == "incumple"]
    desconocidos = [item["nombre"] for item in detalle if item["estado"] == "sin_datos"]
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
