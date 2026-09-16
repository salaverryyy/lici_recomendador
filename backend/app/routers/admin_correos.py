import os
import secrets
import smtplib
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Error as DatabaseError
from psycopg.errors import UniqueViolation
from pydantic import BaseModel, EmailStr, Field

from ..auth import administrador_actual, administrador_escritura, hash_token, password_hash
from ..db import connect
from ..mail import correo_configurado, enviar_correo


router = APIRouter(prefix="/api/admin/correos", tags=["administración: correos"])


class NuevoCorreo(BaseModel):
    email: EmailStr
    contrasena_actual: str = Field(min_length=1)


class ConfirmarContrasena(BaseModel):
    contrasena_actual: str = Field(min_length=1)


class TokenVerificacion(BaseModel):
    token: str = Field(min_length=20, max_length=256)


def comprobar_contrasena(cur, admin_user_id: int, contrasena: str):
    cur.execute("SELECT password_hash FROM admin_users WHERE id = %s AND activo = TRUE", (admin_user_id,))
    usuario = cur.fetchone()
    if not usuario or not password_hash.verify(contrasena, usuario["password_hash"]):
        raise HTTPException(status_code=403, detail="Confirma tu contraseña actual.")


def enviar_verificacion(cur, correo):
    cur.execute(
        """
        SELECT COUNT(*) AS cantidad FROM admin_email_verification_tokens
        WHERE recovery_email_id = %s
          AND creado_en > CURRENT_TIMESTAMP - INTERVAL '1 hour'
        """,
        (correo["id"],),
    )
    if cur.fetchone()["cantidad"] >= 5:
        raise HTTPException(status_code=429, detail="Demasiados envíos. Espera una hora.")
    token = secrets.token_urlsafe(32)
    cur.execute(
        """
        INSERT INTO admin_email_verification_tokens (recovery_email_id, token_hash, expira_en)
        VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '24 hours')
        """,
        (correo["id"], hash_token(token)),
    )
    enlace = os.environ["FRONTEND_URL"].rstrip("/") + "/verificar-correo?token=" + quote(token)
    return correo["email"], enlace


@router.post("/verificar")
def confirmar_correo(datos: TokenVerificacion):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.id AS token_id, c.id AS correo_id
                FROM admin_email_verification_tokens AS t
                JOIN admin_recovery_emails AS c ON c.id = t.recovery_email_id
                WHERE t.token_hash = %s AND t.usado_en IS NULL
                  AND t.expira_en > CURRENT_TIMESTAMP AND c.activo = TRUE
                FOR UPDATE OF t, c
                """,
                (hash_token(datos.token),),
            )
            solicitud = cur.fetchone()
            if solicitud is None:
                raise HTTPException(status_code=400, detail="El enlace no es válido o venció.")
            cur.execute(
                "UPDATE admin_recovery_emails SET verificado_en = CURRENT_TIMESTAMP WHERE id = %s",
                (solicitud["correo_id"],),
            )
            cur.execute(
                """
                UPDATE admin_email_verification_tokens SET usado_en = CURRENT_TIMESTAMP
                WHERE recovery_email_id = %s AND usado_en IS NULL
                """,
                (solicitud["correo_id"],),
            )
            return {"correo_verificado": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo verificar el correo.") from exc


@router.get("")
def ver_correos(sesion=Depends(administrador_actual)):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, email, es_principal, verificado_en IS NOT NULL AS verificado,
                       activo, creado_en
                FROM admin_recovery_emails WHERE admin_user_id = %s ORDER BY es_principal DESC, id
                """,
                (sesion["admin_user_id"],),
            )
            return cur.fetchall()
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo consultar los correos.") from exc


@router.post("", status_code=201)
def agregar_correo(datos: NuevoCorreo, sesion=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            comprobar_contrasena(cur, sesion["admin_user_id"], datos.contrasena_actual)
            cur.execute(
                """
                INSERT INTO admin_recovery_emails (admin_user_id, email)
                VALUES (%s, %s) RETURNING id, email, es_principal, verificado_en, activo
                """,
                (sesion["admin_user_id"], str(datos.email).lower()),
            )
            return {"correo": cur.fetchone(), "mensaje": "Correo agregado; verifica la dirección antes de usarla para recuperar la contraseña."}
    except UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Ese correo ya está registrado.") from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo agregar el correo.") from exc


@router.post("/{correo_id}/enviar-verificacion")
def solicitar_verificacion(correo_id: int, datos: ConfirmarContrasena, sesion=Depends(administrador_escritura)):
    if not correo_configurado():
        raise HTTPException(status_code=503, detail="El envío de correos aún no está configurado.")
    try:
        with connect() as conn, conn.cursor() as cur:
            comprobar_contrasena(cur, sesion["admin_user_id"], datos.contrasena_actual)
            cur.execute(
                """
                SELECT id, email, verificado_en FROM admin_recovery_emails
                WHERE id = %s AND admin_user_id = %s AND activo = TRUE
                """,
                (correo_id, sesion["admin_user_id"]),
            )
            correo = cur.fetchone()
            if correo is None:
                raise HTTPException(status_code=404, detail="Correo no encontrado.")
            if correo["verificado_en"] is not None:
                raise HTTPException(status_code=409, detail="El correo ya está verificado.")
            destinatario, enlace = enviar_verificacion(cur, correo)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo preparar la verificación.") from exc

    try:
        enviar_correo(
            destinatario,
            "Verificar correo de Licitex",
            "Para verificar este correo, abre el enlace durante las próximas 24 horas:\n" + enlace,
        )
    except (RuntimeError, OSError, ValueError, smtplib.SMTPException) as exc:
        raise HTTPException(status_code=503, detail="No se pudo enviar el correo de verificación.") from exc
    return {"verificacion_enviada": True}


@router.put("/{correo_id}/principal")
def cambiar_principal(correo_id: int, datos: ConfirmarContrasena, sesion=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            comprobar_contrasena(cur, sesion["admin_user_id"], datos.contrasena_actual)
            cur.execute("SELECT id FROM admin_users WHERE id = %s FOR UPDATE", (sesion["admin_user_id"],))
            cur.execute(
                """
                SELECT id FROM admin_recovery_emails
                WHERE id = %s AND admin_user_id = %s AND activo = TRUE
                  AND verificado_en IS NOT NULL FOR UPDATE
                """,
                (correo_id, sesion["admin_user_id"]),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="El correo no existe o no está verificado.")
            cur.execute(
                "UPDATE admin_recovery_emails SET es_principal = FALSE WHERE admin_user_id = %s AND es_principal = TRUE",
                (sesion["admin_user_id"],),
            )
            cur.execute(
                "UPDATE admin_recovery_emails SET es_principal = TRUE WHERE id = %s RETURNING id, email",
                (correo_id,),
            )
            return cur.fetchone()
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo cambiar el correo principal.") from exc


@router.delete("/{correo_id}")
def desactivar_correo(correo_id: int, datos: ConfirmarContrasena, sesion=Depends(administrador_escritura)):
    try:
        with connect() as conn, conn.cursor() as cur:
            comprobar_contrasena(cur, sesion["admin_user_id"], datos.contrasena_actual)
            cur.execute(
                """
                UPDATE admin_recovery_emails SET activo = FALSE
                WHERE id = %s AND admin_user_id = %s AND es_principal = FALSE
                  AND activo = TRUE RETURNING id
                """,
                (correo_id, sesion["admin_user_id"]),
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Correo no encontrado o es el principal.")
            return {"correo_id": correo_id, "desactivado": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo desactivar el correo.") from exc
