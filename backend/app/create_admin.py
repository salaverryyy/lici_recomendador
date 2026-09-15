"""Crear el primer administrador desde la terminal, sin publicar credenciales en Git."""

from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError

from .auth import password_hash
from .db import connect


def main():
    username = input("Nombre de administrador: ").strip()
    correo = input("Correo principal de recuperación: ").strip().lower()
    if not username or len(username) > 80:
        raise SystemExit("El nombre debe tener entre 1 y 80 caracteres.")
    try:
        correo = str(TypeAdapter(EmailStr).validate_python(correo))
    except ValidationError as exc:
        raise SystemExit("Escribe un correo válido.") from exc

    contrasena = getpass("Contraseña (mínimo 12 caracteres): ")
    confirmar = getpass("Repite la contraseña: ")
    if len(contrasena) < 12 or contrasena != confirmar:
        raise SystemExit("Las contraseñas deben coincidir y tener al menos 12 caracteres.")

    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM admin_users")
        if cur.fetchone()["total"]:
            raise SystemExit("Ya existe un administrador. Usa el panel o recuperación de contraseña.")
        cur.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s) RETURNING id",
            (username, password_hash.hash(contrasena)),
        )
        admin_id = cur.fetchone()["id"]
        cur.execute(
            """
            INSERT INTO admin_recovery_emails (admin_user_id, email, es_principal)
            VALUES (%s, %s, TRUE)
            """,
            (admin_id, correo),
        )
    print("Administrador creado. El correo queda pendiente de verificación antes de poder recuperar la contraseña.")


if __name__ == "__main__":
    main()
