from io import BytesIO
from typing import Literal
import warnings
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from PIL import Image
from psycopg import Error as DatabaseError
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pypdf import PdfReader

from ..auth import administrador_escritura, administrador_actual
from ..db import connect
from ..storage import guardar, eliminar

router = APIRouter(prefix="/api/admin/equipos", tags=["administración: archivos"])
MAX_FOTOS = 20


class EnlaceArchivo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: Literal["foto", "ficha"]
    url: HttpUrl
    texto_alternativo: str = Field(default="", max_length=250)
    orden: int = Field(default=0, ge=0)


class EditarFoto(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto_alternativo: str | None = Field(default=None, max_length=250)
    orden: int | None = Field(default=None, ge=0)


def bloquear_equipo(cur, id_equipo):
    cur.execute("SELECT id_equipo FROM equipos WHERE id_equipo = %s FOR UPDATE", (id_equipo,))
    if cur.fetchone() is None:
        raise HTTPException(404, "Equipo no encontrado.")


def registrar(id_equipo, tipo, url, alt="", orden=0, storage_key=None):
    anterior = None
    try:
        with connect() as conn, conn.cursor() as cur:
            bloquear_equipo(cur, id_equipo)
            if tipo == "foto":
                cur.execute("SELECT COUNT(*) AS n FROM equipo_archivos WHERE id_equipo=%s AND tipo='foto'", (id_equipo,))
                if cur.fetchone()["n"] >= MAX_FOTOS:
                    raise HTTPException(422, "El equipo admite hasta 20 fotografías.")
            else:
                cur.execute("DELETE FROM equipo_archivos WHERE id_equipo=%s AND tipo='ficha' RETURNING storage_key", (id_equipo,))
                anterior = cur.fetchone()
            cur.execute("""INSERT INTO equipo_archivos(id_equipo, tipo, url, texto_alternativo, orden, storage_key)
                        VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, tipo, url, texto_alternativo, orden""",
                        (id_equipo, tipo, url, alt, orden, storage_key))
            archivo = cur.fetchone()
            if tipo == "ficha":
                cur.execute("UPDATE equipos SET ficha_pdf_url=%s WHERE id_equipo=%s", (url, id_equipo))
            else:
                cur.execute("UPDATE equipos SET imagen_url=COALESCE(imagen_url,%s) WHERE id_equipo=%s", (url, id_equipo))
        if anterior:
            eliminar(anterior["storage_key"])
        return archivo
    except Exception as exc:
        eliminar(storage_key)
        if isinstance(exc, DatabaseError):
            raise HTTPException(503, "No se pudo registrar el archivo.") from exc
        raise


@router.get("/{id_equipo}/archivos")
def listar(id_equipo: str, _=Depends(administrador_actual)):
    try:
        with connect() as conn, conn.cursor() as cur:
            bloquear_equipo(cur, id_equipo)
            cur.execute("SELECT id, tipo, url, texto_alternativo, orden FROM equipo_archivos WHERE id_equipo=%s ORDER BY orden,id", (id_equipo,))
            return cur.fetchall()
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo consultar los archivos.") from exc


@router.post("/{id_equipo}/archivos/enlace", status_code=201)
def agregar_enlace(id_equipo: str, datos: EnlaceArchivo, _=Depends(administrador_escritura)):
    return registrar(id_equipo, datos.tipo, str(datos.url), datos.texto_alternativo, datos.orden)


@router.post("/{id_equipo}/archivos/subir", status_code=201)
def subir(id_equipo: str, tipo: Literal["foto", "ficha"], archivo: UploadFile,
          _=Depends(administrador_escritura)):
    limite = (5 if tipo == "foto" else 20) * 1024 * 1024
    if os.getenv("VERCEL"):
        limite = 3 * 1024 * 1024
    try:
        data = archivo.file.read(limite + 1)
    finally:
        archivo.file.close()
    if not data or len(data) > limite:
        raise HTTPException(422, f"El archivo debe contener datos y no superar {limite // 1024 // 1024} MB.")
    extension, mime = validar_archivo(data, tipo)
    url, key = guardar(data, extension, mime)
    return registrar(id_equipo, tipo, url, storage_key=key)


def validar_archivo(data, tipo):
    # No confiar en el nombre ni en el Content-Type enviados por el navegador.
    try:
        if tipo == "foto":
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as image:
                    formatos = {"JPEG": ("jpg", "image/jpeg"), "PNG": ("png", "image/png"), "WEBP": ("webp", "image/webp")}
                    extension, mime = formatos[image.format]
                    image.verify()
        else:
            if not data.startswith(b"%PDF-"):
                raise ValueError("No es PDF")
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted and not reader.decrypt(""):
                raise ValueError("PDF requiere contraseña")
            if not len(reader.pages):
                raise ValueError("PDF vacío")
            extension, mime = "pdf", "application/pdf"
    except Exception as exc:
        raise HTTPException(422, "Archivo inválido: usa JPG, PNG o WebP para fotos y PDF sin contraseña para fichas.") from exc
    return extension, mime


@router.patch("/{id_equipo}/archivos/{archivo_id}")
def editar(id_equipo: str, archivo_id: int, datos: EditarFoto, _=Depends(administrador_escritura)):
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios or any(v is None for v in cambios.values()):
        raise HTTPException(422, "Indica texto alternativo u orden sin valores null.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(f"UPDATE equipo_archivos SET {', '.join(c+'=%s' for c in cambios)} WHERE id_equipo=%s AND id=%s AND tipo='foto' RETURNING id,tipo,url,texto_alternativo,orden", (*cambios.values(), id_equipo, archivo_id))
            fila = cur.fetchone()
            if fila is None:
                raise HTTPException(404, "Foto no encontrada.")
            return fila
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo editar la foto.") from exc


@router.put("/{id_equipo}/archivos/{archivo_id}/portada")
def portada(id_equipo: str, archivo_id: int, _=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            bloquear_equipo(cur, id_equipo)
            cur.execute("SELECT url FROM equipo_archivos WHERE id_equipo=%s AND id=%s AND tipo='foto'", (id_equipo, archivo_id))
            fila = cur.fetchone()
            if fila is None:
                raise HTTPException(404, "Foto no encontrada.")
            cur.execute("UPDATE equipos SET imagen_url=%s WHERE id_equipo=%s", (fila["url"], id_equipo))
            return {"imagen_url": fila["url"]}
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo cambiar la portada.") from exc


@router.delete("/{id_equipo}/archivos/{archivo_id}")
def quitar(id_equipo: str, archivo_id: int, _=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            bloquear_equipo(cur, id_equipo)
            cur.execute("DELETE FROM equipo_archivos WHERE id_equipo=%s AND id=%s RETURNING *", (id_equipo, archivo_id))
            fila = cur.fetchone()
            if fila is None:
                raise HTTPException(404, "Archivo no encontrado.")
            if fila["tipo"] == "ficha":
                cur.execute("UPDATE equipos SET ficha_pdf_url=NULL WHERE id_equipo=%s AND ficha_pdf_url=%s", (id_equipo, fila["url"]))
            else:
                cur.execute("""UPDATE equipos SET imagen_url=(SELECT url FROM equipo_archivos WHERE id_equipo=%s AND tipo='foto' ORDER BY orden,id LIMIT 1)
                            WHERE id_equipo=%s AND imagen_url=%s""", (id_equipo, id_equipo, fila["url"]))
        eliminar(fila["storage_key"])
        return {"eliminado": True}
    except DatabaseError as exc:
        raise HTTPException(503, "No se pudo quitar el archivo.") from exc
