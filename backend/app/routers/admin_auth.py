import secrets

from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import Error as DatabaseError
from pydantic import BaseModel, Field

from ..auth import (
    SESSION_SECONDS,
    administrador_actual,
    administrador_escritura,
    cookie_name,
    cookie_secure,
    nueva_sesion,
    password_hash,
)
from ..db import connect


router = APIRouter(prefix="/api/admin", tags=["administración: acceso"])
DUMMY_HASH = password_hash.hash(secrets.token_urlsafe(32))


class Credenciales(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=1024)


class CambioContrasena(BaseModel):
    contrasena_actual: str = Field(min_length=1, max_length=1024)
    nueva_contrasena: str = Field(min_length=12, max_length=1024)
    confirmar_contrasena: str = Field(min_length=12, max_length=1024)


@router.post("/login")
def login(datos: Credenciales, response: Response):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS intentos
                FROM admin_login_attempts
                WHERE username = %s AND exitoso = FALSE
                  AND creado_en > CURRENT_TIMESTAMP - INTERVAL '15 minutes'
                """,
                (datos.username,),
            )
            if cur.fetchone()["intentos"] >= 5:
                raise HTTPException(status_code=429, detail="Demasiados intentos. Espera 15 minutos.")

            cur.execute(
                "SELECT id, username, password_hash FROM admin_users WHERE username = %s AND activo = TRUE",
                (datos.username,),
            )
            usuario = cur.fetchone()
            valido = password_hash.verify(
                datos.password,
                usuario["password_hash"] if usuario else DUMMY_HASH,
            )
            cur.execute(
                "INSERT INTO admin_login_attempts (username, exitoso) VALUES (%s, %s)",
                (datos.username, valido and usuario is not None),
            )
            if not valido or usuario is None:
                conn.commit()
                raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

            token, csrf_token = nueva_sesion(cur, usuario["id"])
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo iniciar sesión.") from exc

    response.set_cookie(
        key=cookie_name(),
        value=token,
        max_age=SESSION_SECONDS,
        httponly=True,
        secure=cookie_secure(),
        samesite="strict",
        path="/",
    )
    return {"username": usuario["username"], "csrf_token": csrf_token}


@router.get("/sesion")
def sesion_actual(sesion=Depends(administrador_actual)):
    return {"username": sesion["username"], "csrf_token": sesion["csrf_token"]}


@router.post("/logout")
def logout(response: Response, sesion=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE admin_sessions SET revocado_en = CURRENT_TIMESTAMP WHERE id = %s",
                (sesion["session_id"],),
            )
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo cerrar la sesión.") from exc
    response.delete_cookie(key=cookie_name(), path="/", secure=cookie_secure())
    return {"sesion_cerrada": True}


@router.put("/contrasena")
def cambiar_contrasena(datos: CambioContrasena, response: Response, sesion=Depends(administrador_escritura)):
    if datos.nueva_contrasena != datos.confirmar_contrasena:
        raise HTTPException(status_code=422, detail="Las dos contraseñas deben coincidir.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM admin_users WHERE id = %s AND activo = TRUE FOR UPDATE",
                (sesion["admin_user_id"],),
            )
            usuario = cur.fetchone()
            if not usuario or not password_hash.verify(datos.contrasena_actual, usuario["password_hash"]):
                raise HTTPException(status_code=403, detail="Contraseña actual incorrecta.")
            cur.execute(
                "UPDATE admin_users SET password_hash = %s WHERE id = %s",
                (password_hash.hash(datos.nueva_contrasena), sesion["admin_user_id"]),
            )
            cur.execute(
                """
                UPDATE admin_sessions SET revocado_en = CURRENT_TIMESTAMP
                WHERE admin_user_id = %s AND revocado_en IS NULL
                """,
                (sesion["admin_user_id"],),
            )
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo cambiar la contraseña.") from exc
    response.delete_cookie(key=cookie_name(), path="/", secure=cookie_secure())
    return {"contrasena_actualizada": True, "mensaje": "Vuelve a iniciar sesión."}
