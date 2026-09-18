import math
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Error as DatabaseError
from psycopg.errors import CheckViolation, ForeignKeyViolation, UniqueViolation
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ..auth import administrador_actual, administrador_escritura
from ..db import connect
from ..storage import eliminar as eliminar_archivo


router = APIRouter(prefix="/api/admin/equipos", tags=["administración: equipos"])


class NuevoEquipo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id_equipo: str = Field(min_length=3, max_length=100, pattern="^[A-Z0-9-]+$")
    marca: str = Field(min_length=1, max_length=120)
    modelo: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=80)
    descripcion: str | None = None
    anio_modelo: int | None = Field(default=None, ge=1900, le=2200)
    imagen_url: HttpUrl | None = None
    modelo_3d_url: HttpUrl | None = None
    ficha_pdf_url: HttpUrl | None = None
    web_url: HttpUrl | None = None
    publicado: bool = True


class CambiosEquipo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    marca: str | None = Field(default=None, min_length=1, max_length=120)
    modelo: str | None = Field(default=None, min_length=1, max_length=120)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    descripcion: str | None = None
    anio_modelo: int | None = Field(default=None, ge=1900, le=2200)
    imagen_url: HttpUrl | None = None
    modelo_3d_url: HttpUrl | None = None
    ficha_pdf_url: HttpUrl | None = None
    web_url: HttpUrl | None = None
    publicado: bool | None = None


class CambiosEspecificaciones(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cambios: dict[str, Any] = Field(min_length=1)


class RangoRadio(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    frecuencia_min_mhz: float = Field(ge=0)
    frecuencia_max_mhz: float = Field(ge=0)


BOOLEANOS = {
    "tiene_imu", "tiene_camara", "sim_4g", "laser", "bateria_intercambiable",
    "bateria_caliente", "gps", "glonass", "galileo", "beidou", "qzss",
    "navic_irnss", "sbas", "tiene_snlonglink",
}
ENTEROS = {"canales_gnss", "peso_max", "tiempo_inicializacion", "cantidad_camaras"}
NUMERICOS = {
    "memoria", "mp_camara", "autonomia_bateria", "rtk_horizontal_mm",
    "rtk_vertical_mm", "rtk_ppm_h", "rtk_ppm_v", "static_horizontal_mm",
    "static_vertical_mm", "static_ppm_h", "static_ppm_v", "largo_mm", "ancho_mm",
    "alto_mm", "ppp_h_cm", "ppp_v_cm",
}
TEMPERATURAS = {'temperatura_almacenamiento_min_c', 'temperatura_operacion_max_c', 'temperatura_almacenamiento_max_c', 'temperatura_camara_min_c', 'temperatura_operacion_min_c', 'temperatura_camara_max_c'}
NUMERICOS |= {'caida_m', 'humedad_max_pct'}
TEXTOS = {'ambiental_notas', 'radio_frecuencia', 'proteccion_ip', 'choque_condiciones', 'ambiental_fuente', 'caida_condiciones', 'vibracion_norma', 'humedad_condicion'}
BOOLEANOS |= {"memoria_expandible", "bluetooth", "wifi", "uhf_tx_rx_integrada", "lte_4g",
              "radio_potencia_ajustable", "protocolo_multimarca", "bateria_interna",
              "registro_rinex", "registro_rinex_3", "registro_propietario"}
NUMERICOS |= {"memoria_expandida_max_gb", "memoria_opcional_fabrica_max_gb", "radio_potencia_max_w"}
TEXTOS |= {"imu_generacion", "imu_tecnologia", "bluetooth_version", "wifi_estandar", "uhf_modo",
           "radio_protocolos", "tipo_bateria", "rinex_versiones", "formato_propietario", "tecnica_notas", "tecnica_fuente"}
EDITABLES = BOOLEANOS | ENTEROS | NUMERICOS | TEXTOS | TEMPERATURAS
BOOLEANOS |= {'lemo','usb','usb_c','rs232'}
NUMERICOS |= {'actualizacion_hz','inclinacion_imu_deg'}
ENTEROS.add('baterias_incluidas_por_receptor')
TEXTOS |= {'auditoria_fuente','auditoria_notas'}
ENTEROS |= {'cantidad_baterias','cantidad_baterias_kit','lemo_pines'}
TEXTOS |= {'baterias_conectores_fuente','baterias_conectores_notas'}
NUMERICOS |= {'red_'+k for k in ('rtk_horizontal_mm','rtk_vertical_mm','rtk_ppm_h','rtk_ppm_v')}
NUMERICOS |= {'largo_'+k for k in ('static_horizontal_mm','static_vertical_mm','static_ppm_h','static_ppm_v')}
EDITABLES = BOOLEANOS | ENTEROS | NUMERICOS | TEXTOS | TEMPERATURAS
CONSTELACIONES = ("gps", "glonass", "galileo", "beidou", "qzss", "navic_irnss")


def validar_especificaciones(cambios: dict[str, Any]):
    desconocidos = set(cambios) - EDITABLES
    if desconocidos:
        raise HTTPException(status_code=422, detail={"campos_no_editables": sorted(desconocidos)})
    for campo, valor in cambios.items():
        if valor is None:
            continue
        if campo in BOOLEANOS and type(valor) is not bool:
            raise HTTPException(status_code=422, detail=f"{campo} debe ser booleano o null.")
        if campo in ENTEROS and (type(valor) is not int or valor < 0):
            raise HTTPException(status_code=422, detail=f"{campo} debe ser entero no negativo o null.")
        if campo in {'cantidad_baterias','cantidad_baterias_kit','lemo_pines','baterias_incluidas_por_receptor'} and valor < 1:
            raise HTTPException(422,f'{campo} debe ser un entero positivo o null.')
        if campo in NUMERICOS and (type(valor) not in (int, float) or not math.isfinite(valor) or valor < 0):
            raise HTTPException(status_code=422, detail=f"{campo} debe ser numérico no negativo o null.")
        if campo in TEMPERATURAS and (type(valor) not in (int, float) or not math.isfinite(valor) or not -273.15 <= valor <= 200):
            raise HTTPException(422, "Temperatura inválida; usa grados Celsius entre -273.15 y 200.")
        if campo == "humedad_max_pct" and type(valor) in (int, float) and valor > 100:
            raise HTTPException(422, "La humedad no puede superar 100%.")
        if campo == 'inclinacion_imu_deg' and valor > 180:
            raise HTTPException(422, 'La inclinación no puede superar 180°.')
        if campo == "proteccion_ip" and (type(valor) is not str or not re.fullmatch(r"IP[0-6][0-9](?: \| IP[0-6][0-9])*", valor)):
            raise HTTPException(422, "Usa un código IP, por ejemplo IP67 o IP66 | IP68.")
        if campo in TEXTOS and (type(valor) is not str or len(valor) > 500):
            raise HTTPException(status_code=422, detail=f"{campo} debe ser texto corto o null.")


def validar_rango(datos: RangoRadio):
    if datos.frecuencia_min_mhz > datos.frecuencia_max_mhz:
        raise HTTPException(status_code=422, detail="La frecuencia mínima supera la máxima.")


@router.get("")
def listar_admin(_=Depends(administrador_actual)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM equipos ORDER BY marca, modelo")
            return cur.fetchall()
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar los equipos.") from exc


@router.get("/{id_equipo}")
def detalle_admin(id_equipo: str, _=Depends(administrador_actual)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM equipos WHERE id_equipo = %s", (id_equipo,))
            equipo = cur.fetchone()
            if equipo is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")
            cur.execute("SELECT * FROM base_evaluacion WHERE id_equipo = %s", (id_equipo,))
            evaluacion = cur.fetchone()
            controladora = None
            if equipo['categoria'] == 'Controladora':
                cur.execute('SELECT * FROM controladora_especificaciones WHERE id_equipo=%s', (id_equipo,))
                controladora = cur.fetchone()
            cur.execute(
                """
                SELECT id, frecuencia_min_mhz, frecuencia_max_mhz
                FROM equipo_radio_frecuencia WHERE id_equipo = %s ORDER BY id
                """,
                (id_equipo,),
            )
            return {"equipo": equipo, "evaluacion": evaluacion, "controladora": controladora, "radio_frecuencias": cur.fetchall()}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar el equipo.") from exc


@router.post("", status_code=201)
def crear_equipo(datos: NuevoEquipo, _=Depends(administrador_escritura)):
    valores = datos.model_dump(mode="json")
    columnas = list(valores)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO equipos ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(columnas))}) RETURNING *",
                list(valores.values()),
            )
            return cur.fetchone()
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Ya existe un equipo con ese ID.") from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo crear el equipo.") from exc


@router.patch("/{id_equipo}")
def editar_equipo(id_equipo: str, datos: CambiosEquipo, _=Depends(administrador_escritura)):
    cambios = datos.model_dump(mode="json", exclude_unset=True)
    if not cambios:
        raise HTTPException(status_code=422, detail="Indica al menos un campo para editar.")
    if any(cambios.get(campo) is None for campo in ("marca", "modelo", "categoria", "publicado") if campo in cambios):
        raise HTTPException(status_code=422, detail="Marca, modelo, categoría y publicado no pueden ser null.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE equipos SET {', '.join(f'{campo} = %s' for campo in cambios)} WHERE id_equipo = %s RETURNING *",
                [*cambios.values(), id_equipo],
            )
            actualizado = cur.fetchone()
            if actualizado is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")
            return actualizado
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo editar el equipo.") from exc


@router.put("/{id_equipo}")
def reemplazar_datos_equipo(id_equipo: str, datos: CambiosEquipo, _=Depends(administrador_escritura)):
    return editar_equipo(id_equipo, datos, _)


@router.delete("/{id_equipo}")
def eliminar_equipo(id_equipo: str, _=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT id_equipo FROM equipos WHERE id_equipo=%s FOR UPDATE", (id_equipo,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")
            cur.execute("SELECT storage_key FROM equipo_archivos WHERE id_equipo=%s AND storage_key IS NOT NULL", (id_equipo,))
            archivos = cur.fetchall()
            cur.execute("DELETE FROM equipos WHERE id_equipo = %s RETURNING id_equipo", (id_equipo,))
            eliminado = cur.fetchone()
            if eliminado is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")
        for archivo in archivos:
            eliminar_archivo(archivo["storage_key"])
        return {"id_equipo": eliminado["id_equipo"], "eliminado": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo eliminar el equipo.") from exc


@router.patch("/{id_equipo}/especificaciones")
def editar_especificaciones(id_equipo: str, datos: CambiosEspecificaciones, _=Depends(administrador_escritura)):
    cambios = dict(datos.cambios)
    validar_especificaciones(cambios)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT id_equipo FROM equipos WHERE id_equipo = %s FOR UPDATE", (id_equipo,))
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Equipo no encontrado.")
            cur.execute(
                "INSERT INTO base_evaluacion (id_equipo) VALUES (%s) ON CONFLICT (id_equipo) DO NOTHING",
                (id_equipo,),
            )
            cur.execute("SELECT * FROM base_evaluacion WHERE id_equipo = %s FOR UPDATE", (id_equipo,))
            actuales = cur.fetchone()
            combinados = {**actuales, **cambios}
            for prefijo in ("operacion", "almacenamiento", "camara"):
                minimo = combinados.get(f"temperatura_{prefijo}_min_c")
                maximo = combinados.get(f"temperatura_{prefijo}_max_c")
                if minimo is not None and maximo is not None and minimo > maximo:
                    raise HTTPException(422, "La temperatura mínima supera la máxima.")
            if "cantidad_camaras" in cambios and cambios["cantidad_camaras"] is not None:
                presencia = cambios["cantidad_camaras"] > 0
                if "tiene_camara" in cambios and cambios["tiene_camara"] is not presencia:
                    raise HTTPException(422, "La cantidad de cámaras contradice el indicador de cámara.")
                cambios["tiene_camara"] = presencia
            elif cambios.get("tiene_camara") is False:
                cambios["cantidad_camaras"] = 0
            elif cambios.get("tiene_camara") is True and actuales.get("cantidad_camaras") == 0:
                cambios["cantidad_camaras"] = None
            if any(campo in cambios for campo in CONSTELACIONES):
                cambios["constelaciones"] = sum(
                    (cambios.get(campo, actuales[campo]) is True) for campo in CONSTELACIONES
                )
            if "ppp_h_cm" in cambios or "ppp_v_cm" in cambios:
                cambios["tiene_ppp"] = (
                    cambios.get("ppp_h_cm", actuales["ppp_h_cm"]) is not None
                    or cambios.get("ppp_v_cm", actuales["ppp_v_cm"]) is not None
                )
            cur.execute(
                f"UPDATE base_evaluacion SET {', '.join(f'{campo} = %s' for campo in cambios)} WHERE id_equipo = %s RETURNING *",
                [*cambios.values(), id_equipo],
            )
            return cur.fetchone()
    except CheckViolation as exc:
        raise HTTPException(status_code=422, detail="Una especificación no cumple las restricciones de la tabla.") from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo editar las especificaciones.") from exc


@router.post("/{id_equipo}/radio", status_code=201)
def agregar_radio(id_equipo: str, datos: RangoRadio, _=Depends(administrador_escritura)):
    validar_rango(datos)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO equipo_radio_frecuencia (id_equipo, frecuencia_min_mhz, frecuencia_max_mhz)
                VALUES (%s, %s, %s) RETURNING *
                """,
                (id_equipo, datos.frecuencia_min_mhz, datos.frecuencia_max_mhz),
            )
            return cur.fetchone()
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Ese rango ya está registrado.") from exc
    except ForeignKeyViolation as exc:
        raise HTTPException(status_code=404, detail="Equipo no encontrado.") from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo agregar la radio.") from exc


@router.put("/{id_equipo}/radio/{radio_id}")
def editar_radio(id_equipo: str, radio_id: int, datos: RangoRadio, _=Depends(administrador_escritura)):
    validar_rango(datos)
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE equipo_radio_frecuencia
                SET frecuencia_min_mhz = %s, frecuencia_max_mhz = %s
                WHERE id = %s AND id_equipo = %s RETURNING *
                """,
                (datos.frecuencia_min_mhz, datos.frecuencia_max_mhz, radio_id, id_equipo),
            )
            actualizado = cur.fetchone()
            if actualizado is None:
                raise HTTPException(status_code=404, detail="Rango no encontrado.")
            return actualizado
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Ese rango ya está registrado.") from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo editar la radio.") from exc


@router.delete("/{id_equipo}/radio/{radio_id}")
def eliminar_radio(id_equipo: str, radio_id: int, _=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM equipo_radio_frecuencia WHERE id = %s AND id_equipo = %s RETURNING id",
                (radio_id, id_equipo),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Rango no encontrado.")
            return {"radio_id": radio_id, "eliminado": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo eliminar la radio.") from exc
