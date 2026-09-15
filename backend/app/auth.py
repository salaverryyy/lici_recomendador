import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Request
from psycopg import Error as DatabaseError
from pwdlib import PasswordHash

from .db import connect


password_hash = PasswordHash.recommended()
SESSION_SECONDS = 12 * 60 * 60


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def cookie_secure() -> bool:
    return os.getenv("SESSION_COOKIE_SECURE", "true" if os.getenv("VERCEL") else "false").lower() == "true"


def cookie_name() -> str:
    return "__Host-admin_session" if cookie_secure() else "admin_session"


def nueva_sesion(cur, admin_user_id: int):
    token = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    expira_en = datetime.now(timezone.utc) + timedelta(seconds=SESSION_SECONDS)
    cur.execute(
        """
        INSERT INTO admin_sessions (admin_user_id, token_hash, csrf_token, expira_en)
        VALUES (%s, %s, %s, %s)
        """,
        (admin_user_id, hash_token(token), csrf_token, expira_en),
    )
    return token, csrf_token


def administrador_actual(request: Request):
    token = request.cookies.get(cookie_name())
    if not token:
        raise HTTPException(status_code=401, detail="Inicia sesión como administrador.")
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.id AS session_id, s.csrf_token, u.id AS admin_user_id, u.username
                FROM admin_sessions AS s
                JOIN admin_users AS u ON u.id = s.admin_user_id
                WHERE s.token_hash = %s AND s.expira_en > CURRENT_TIMESTAMP
                  AND s.revocado_en IS NULL AND u.activo = TRUE
                """,
                (hash_token(token),),
            )
            sesion = cur.fetchone()
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="No se pudo verificar la sesión.") from exc
    if sesion is None:
        raise HTTPException(status_code=401, detail="La sesión no está vigente.")
    return sesion


def administrador_escritura(
    sesion=Depends(administrador_actual),
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    if not csrf_token or not hmac.compare_digest(csrf_token, sesion["csrf_token"]):
        raise HTTPException(status_code=403, detail="Falta el token de protección del formulario.")
    return sesion
