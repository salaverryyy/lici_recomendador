"""Subidas por fragmentos: ninguna petición transporta más de 2 MiB."""
import base64
import hashlib
import hmac
import json
import logging
import math
import os
import re
import time
from uuid import uuid4
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from ..auth import administrador_actual, administrador_escritura
from ..db import connect
from ..storage import cliente_s3, modo, UPLOAD_DIR, guardar
from .admin_archivos import bloquear_equipo, registrar, validar_archivo

router = APIRouter(prefix='/api/admin', tags=['administración: almacenamiento'])
CHUNK = 2 * 1024 * 1024

class Inicio(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tipo: Literal['foto','ficha']
    bytes: int = Field(gt=0,le=20*1024*1024)

class Operacion(BaseModel):
    token: str = Field(max_length=2000)

def firmar(datos, sesion):
    payload = base64.urlsafe_b64encode(json.dumps(datos).encode()).decode()
    signature = hmac.new(sesion['csrf_token'].encode(),payload.encode(),hashlib.sha256).hexdigest()
    return payload+'.'+signature

def verificar(token, sesion, permitir_expirado=False):
    try:
        payload, signature = token.split('.')
        expected = hmac.new(sesion['csrf_token'].encode(),payload.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,signature): raise ValueError()
        datos = json.loads(base64.urlsafe_b64decode(payload))
        if not re.fullmatch(r'[a-f0-9]{32}',datos['id']): raise ValueError()
        if not permitir_expirado and datos['expira'] < time.time(): raise ValueError()
        if not 0 < datos['bytes'] <= (5 if datos['tipo']=='foto' else 20)*1024*1024: raise ValueError()
        return datos
    except Exception as exc:
        raise HTTPException(422,'La subida no es válida o expiró. Vuelve a cargar el archivo.') from exc

def ruta(datos, numero):
    return f"subidas-temporales/{datos['id']}/{numero}"

def limpiar(datos):
    try:
        for n in range(math.ceil(datos['bytes']/CHUNK)):
            key = ruta(datos,n)
            if modo()=='s3': cliente_s3().delete_object(Bucket=os.environ['S3_BUCKET'],Key=key)
            else: (UPLOAD_DIR/key).unlink(missing_ok=True)
    except Exception:
        logging.getLogger(__name__).exception('No se pudieron limpiar fragmentos temporales')

@router.get('/almacenamiento')
def uso(_=Depends(administrador_actual)):
    try:
        total = count = 0
        provider = modo()
        if provider=='s3':
            for page in cliente_s3().get_paginator('list_objects_v2').paginate(Bucket=os.environ['S3_BUCKET']):
                for obj in page.get('Contents',[]):
                    total += obj['Size']; count += 1
        else:
            for path in UPLOAD_DIR.rglob('*'):
                if path.is_file(): total += path.stat().st_size; count += 1
        return {'bytes':total,'archivos':count,'referencia_bytes':10_000_000_000,'proveedor':provider}
    except Exception as exc:
        raise HTTPException(503,'No se pudo consultar el espacio del almacenamiento.') from exc

@router.post('/equipos/{id_equipo}/archivos/iniciar')
def iniciar(id_equipo: str, datos: Inicio, sesion=Depends(administrador_escritura)):
    if datos.tipo=='foto' and datos.bytes > 5*1024*1024:
        raise HTTPException(422,'Las fotos admiten hasta 5 MB; las fichas PDF hasta 20 MB.')
    with connect() as conn, conn.cursor() as cur: bloquear_equipo(cur,id_equipo)
    manifest = {'id':uuid4().hex,'equipo':id_equipo,'tipo':datos.tipo,'bytes':datos.bytes,'expira':time.time()+1800}
    return {'token':firmar(manifest,sesion),'fragmento_bytes':CHUNK}

@router.put('/archivos/fragmento/{numero}')
async def fragmento(numero: int, token: str, request: Request, sesion=Depends(administrador_escritura)):
    datos = verificar(token,sesion)
    if not 0 <= numero < math.ceil(datos['bytes']/CHUNK): raise HTTPException(422,'Fragmento inválido.')
    expected = min(CHUNK,datos['bytes']-numero*CHUNK)
    data = bytearray()
    async for block in request.stream():
        data.extend(block)
        if len(data)>expected: raise HTTPException(422,'Fragmento demasiado grande.')
    if len(data)!=expected: raise HTTPException(422,'Fragmento incompleto.')
    try:
        key = ruta(datos,numero)
        if modo()=='s3': cliente_s3().put_object(Bucket=os.environ['S3_BUCKET'],Key=key,Body=bytes(data),ContentType='application/octet-stream')
        else:
            path=UPLOAD_DIR/key; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
        return {'recibido':numero}
    except Exception as exc: raise HTTPException(503,'No se pudo cargar el fragmento.') from exc

@router.post('/archivos/finalizar',status_code=201)
def finalizar(op: Operacion, sesion=Depends(administrador_escritura)):
    datos = verificar(op.token,sesion)
    try:
        data = bytearray()
        for n in range(math.ceil(datos['bytes']/CHUNK)):
            expected=min(CHUNK,datos['bytes']-n*CHUNK)
            if modo()=='s3':
                response=cliente_s3().get_object(Bucket=os.environ['S3_BUCKET'],Key=ruta(datos,n))
                body=response['Body']
                try: block=body.read(expected+1)
                finally: body.close()
            else:
                with (UPLOAD_DIR/ruta(datos,n)).open('rb') as body: block=body.read(expected+1)
            if len(block)!=expected: raise HTTPException(422,'Faltan fragmentos del archivo. Vuelve a cargarlo.')
            data.extend(block)
        extension,mime=validar_archivo(bytes(data),datos['tipo'])
        url,key=guardar(bytes(data),extension,mime)
        return registrar(datos['equipo'],datos['tipo'],url,storage_key=key)
    except HTTPException: raise
    except Exception as exc: raise HTTPException(503,'No se pudo finalizar la subida. Vuelve a cargar el archivo.') from exc
    finally: limpiar(datos)

@router.post('/archivos/cancelar')
def cancelar(op: Operacion,sesion=Depends(administrador_escritura)):
    limpiar(verificar(op.token,sesion,permitir_expirado=True))
    return {'cancelado':True}
