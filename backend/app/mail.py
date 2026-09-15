import os
import smtplib
import ssl
from email.message import EmailMessage


def correo_configurado() -> bool:
    return all(os.getenv(nombre) for nombre in (
        "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM", "FRONTEND_URL"
    ))


def enviar_correo(destinatario: str, asunto: str, texto: str):
    if not correo_configurado():
        raise RuntimeError("El proveedor de correo aún no está configurado.")
    puerto = int(os.environ["SMTP_PORT"])
    if puerto not in (465, 587):
        raise RuntimeError("Configura SMTP en puerto 465 o 587.")

    mensaje = EmailMessage()
    mensaje["From"] = os.environ["SMTP_FROM"]
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(texto)

    contexto = ssl.create_default_context()
    if puerto == 465:
        with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], puerto, context=contexto, timeout=10) as smtp:
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            smtp.send_message(mensaje)
    else:
        with smtplib.SMTP(os.environ["SMTP_HOST"], puerto, timeout=10) as smtp:
            smtp.starttls(context=contexto)
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            smtp.send_message(mensaje)
