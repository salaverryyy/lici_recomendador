"""Archivos locales en desarrollo o almacenamiento compatible con S3 en producción."""
import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"


def modo():
    value = os.getenv("MEDIA_STORAGE", "s3" if os.getenv("VERCEL") else "local")
    if value not in ("local", "s3") or (os.getenv("VERCEL") and value == "local"):
        raise HTTPException(503, "Configura almacenamiento persistente para los archivos.")
    return value


def cliente_s3():
    import boto3
    if not os.getenv("S3_BUCKET") or not os.getenv("MEDIA_PUBLIC_URL"):
        raise HTTPException(503, "El almacenamiento de archivos todavía no está configurado.")
    return boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL") or None,
                        region_name=os.getenv("AWS_DEFAULT_REGION", "auto"))


def guardar(data: bytes, extension: str, content_type: str):
    key = f"equipos/{uuid4().hex}.{extension}"
    try:
        if modo() == "s3":
            cliente_s3().put_object(Bucket=os.environ["S3_BUCKET"], Key=key, Body=data,
                                   ContentType=content_type)
            return os.environ["MEDIA_PUBLIC_URL"].rstrip("/") + "/" + key, "s3:" + key
        destino = UPLOAD_DIR / key
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(data)
        return "/archivos/" + key, "local:" + key
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(503, "No se pudo guardar el archivo.") from exc


def eliminar(key: str | None):
    # Solo eliminar objetos creados por nosotros, nunca URLs externas.
    if not key:
        return
    provider, _, nombre = key.partition(":")
    if not nombre.startswith("equipos/") or ".." in nombre or "\\" in nombre:
        return
    try:
        if provider == "s3":
            cliente_s3().delete_object(Bucket=os.environ["S3_BUCKET"], Key=nombre)
        elif provider == "local":
            (UPLOAD_DIR / nombre).unlink(missing_ok=True)
    except Exception:
        logging.getLogger(__name__).exception("No se pudo limpiar un archivo de almacenamiento")
