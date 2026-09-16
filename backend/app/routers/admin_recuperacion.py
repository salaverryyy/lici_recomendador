import logging
import os
import secrets
import smtplib
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from psycopg import Error as DatabaseError
from pydantic import BaseModel, EmailStr, Field

from ..auth import hash_token, password_hash
from ..db import connect
from ..mail import correo_configurado, enviar_correo


router = APIRouter(prefix="/api/admin/recuperacion", tags=["administración: recuperación"])
logger = logging.getLogger(__name__)


class SolicitudRecuperacion(BaseModel):
    email: EmailStr


class NuevaContrasena(BaseModel):
    token: str = Field(min_length=20, max_length=256)
    nueva_contrasena: str = Field(min_length=12, max_length=1024)
    confirmar_contrasena: str = Field(min_length=12, max_length=1024)


@router.post("/solicitar", status_code=202)
def solicitar_recuperacion(datos: SolicitudRecuperacion):
    if not correo_configurado():
        raise HTTPException(status_code=503, detail="El envío de correos aún no está configurado.")

    destinatario = None
    enlace = None
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.email
                FROM admin_recovery_emails AS c
                JOIN admin_users AS u ON u.id = c.admin_user_id
                WHERE LOWER(c.email) = LOWER(%s) AND c.activo = TRUE
                  AND c.verificado_en IS NOT NULL AND u.activo = TRUE
                """,
                (str(datos.email),),
            )
            correo = cur.fetchone()
            if correo:
                cur.execute(
                    """
                    SELECT COUNT(*) AS cantidad FROM admin_password_reset_tokens
                    WHERE recovery_email_id = %s
                      AND creado_en > CURRENT_TIMESTAMP - INTERVAL '1 hour'
                    """,
                    (correo["id"],),
                )
                if cur.fetchone()["cantidad"] < 5:
                    token = secrets.token_urlsafe(32)
                    cur.execute(
                        """
                        INSERT INTO admin_password_reset_tokens (recovery_email_id, token_hash, expira_en)
                        VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '30 minutes')
                        """,
                        (correo["id"], hash_token(token)),
                    )
                    destinatario = correo["email"]
                    enlace = os.environ["FRONTEND_URL"].rstrip("/") + "/restablecer?token=" + quote(token)
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo procesar la solicitud.") from exc

    if destinatario:
        try:
            enviar_correo(
                destinatario,
                "Restablecer contraseña de Licitex",
                "Para restablecer la contraseña, abre este enlace durante los próximos 30 minutos:\n"
                + enlace + "\nSi no lo solicitaste, ignora este mensaje.",
            )
        except (RuntimeError, OSError, ValueError, smtplib.SMTPException) as exc:
            logger.warning("No se pudo enviar un correo de recuperación: %s", type(exc).__name__)
    return {"mensaje": "Si el correo está registrado y verificado, recibirás un enlace de recuperación."}


@router.post("/confirmar")
def confirmar_recuperacion(datos: NuevaContrasena):
    if datos.nueva_contrasena != datos.confirmar_contrasena:
        raise HTTPException(status_code=422, detail="Las dos contraseñas deben coincidir.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT t.id AS token_id, u.id AS admin_user_id
                FROM admin_password_reset_tokens AS t
                JOIN admin_recovery_emails AS c ON c.id = t.recovery_email_id
                JOIN admin_users AS u ON u.id = c.admin_user_id
                WHERE t.token_hash = %s AND t.usado_en IS NULL
                  AND t.expira_en > CURRENT_TIMESTAMP
                  AND c.activo = TRUE AND c.verificado_en IS NOT NULL
                  AND u.activo = TRUE
                FOR UPDATE OF t, u
                """,
                (hash_token(datos.token),),
            )
            solicitud = cur.fetchone()
            if solicitud is None:
                raise HTTPException(status_code=400, detail="El enlace no es válido o venció.")
            cur.execute(
                "UPDATE admin_users SET password_hash = %s WHERE id = %s",
                (password_hash.hash(datos.nueva_contrasena), solicitud["admin_user_id"]),
            )
            cur.execute(
                """
                UPDATE admin_password_reset_tokens SET usado_en = CURRENT_TIMESTAMP
                WHERE recovery_email_id IN (
                    SELECT id FROM admin_recovery_emails WHERE admin_user_id = %s
                ) AND usado_en IS NULL
                """,
                (solicitud["admin_user_id"],),
            )
            cur.execute(
                """
                UPDATE admin_sessions SET revocado_en = CURRENT_TIMESTAMP
                WHERE admin_user_id = %s AND revocado_en IS NULL
                """,
                (solicitud["admin_user_id"],),
            )
            return {"contrasena_actualizada": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo actualizar la contraseña.") from exc
