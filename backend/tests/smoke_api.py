"""Prueba integrada con datos temporales; limpia equipo, administrador y regla al terminar."""

import secrets
from io import BytesIO
from PIL import Image
from pypdf import PdfWriter

import httpx

from app.auth import hash_token, password_hash
from app.db import connect
from app.storage import eliminar as eliminar_archivo


API = "http://127.0.0.1:8000"
SUFIJO = secrets.token_hex(4).upper()
USERNAME = "codex_smoke_" + SUFIJO.lower()
PASSWORD = secrets.token_urlsafe(24)
ID_EQUIPO = "GNSS-CODEX-SMOKE-" + SUFIJO


def comprobar(respuesta, esperado):
    assert respuesta.status_code == esperado, (respuesta.request.method, respuesta.request.url, respuesta.status_code, respuesta.text[:300])
    return respuesta.json()


def main():
    admin_id = None
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT criterio, peso, activo FROM reglas_recomendacion WHERE criterio = 'tiene_imu'")
        regla_original = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS n FROM equipos")
        total_original = cur.fetchone()["n"]

    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO admin_users (username, password_hash) VALUES (%s, %s) RETURNING id",
                (USERNAME, password_hash.hash(PASSWORD)),
            )
            admin_id = cur.fetchone()["id"]
            cur.execute(
                "INSERT INTO admin_recovery_emails (admin_user_id, email, es_principal) VALUES (%s, %s, TRUE) RETURNING id",
                (admin_id, f"{USERNAME}@example.com"),
            )
            correo_principal_id = cur.fetchone()["id"]

        with httpx.Client(base_url=API, timeout=15) as client:
            comprobar(client.get("/api/admin/equipos"), 401)
            comprobar(client.post("/api/admin/login", json={"username": USERNAME, "password": "incorrecta"}), 401)
            login = comprobar(client.post("/api/admin/login", json={"username": USERNAME, "password": PASSWORD}), 200)
            csrf = login["csrf_token"]
            headers = {"X-CSRF-Token": csrf}
            datos_equipo = {"id_equipo": ID_EQUIPO, "marca": "Codex", "modelo": "Prueba", "categoria": "GNSS"}
            comprobar(client.post("/api/admin/equipos", json=datos_equipo), 403)
            comprobar(client.post("/api/admin/equipos", json=datos_equipo, headers=headers), 201)
            comprobar(client.post("/api/admin/equipos", json=datos_equipo, headers=headers), 409)
            archivos_url = f"/api/admin/equipos/{ID_EQUIPO}/archivos"
            comprobar(client.get(archivos_url), 200)
            comprobar(client.post(archivos_url + "/enlace", json={"tipo": "foto", "url": "https://example.com/foto.jpg"}), 403)
            comprobar(client.post(archivos_url + "/enlace", json={"tipo": "foto", "url": "javascript:alert(1)"}, headers=headers), 422)
            foto = comprobar(client.post(archivos_url + "/enlace", json={"tipo": "foto", "url": "https://example.com/foto.jpg", "texto_alternativo": "Equipo de prueba"}, headers=headers), 201)
            comprobar(client.patch(archivos_url + f"/{foto['id']}", json={"orden": 2}, headers=headers), 200)
            imagen = BytesIO()
            Image.new("RGB", (8, 8), "white").save(imagen, format="PNG")
            subir_url = archivos_url + "/subir"
            comprobar(client.post(subir_url, params={"tipo": "foto"}, files={"archivo": ("falsa.png", b"no es imagen", "image/png")}, headers=headers), 422)
            subida = comprobar(client.post(subir_url, params={"tipo": "foto"}, files={"archivo": ("foto.png", imagen.getvalue(), "image/png")}, headers=headers), 201)
            assert client.get(subida["url"]).status_code == 200
            comprobar(client.put(archivos_url + f"/{subida['id']}/portada", headers=headers), 200)
            detalle = comprobar(client.get(f"/api/equipos/{ID_EQUIPO}"), 200)
            assert len(detalle["fotografias"]) == 2 and detalle["equipo"]["imagen_url"] == subida["url"]
            comprobar(client.delete(archivos_url + f"/{subida['id']}", headers=headers), 200)
            assert client.get(subida["url"]).status_code == 404
            assert comprobar(client.get(f"/api/equipos/{ID_EQUIPO}"), 200)["equipo"]["imagen_url"] == foto["url"]
            documento = BytesIO()
            writer = PdfWriter()
            writer.add_blank_page(width=100, height=100)
            writer.write(documento)
            ficha = comprobar(client.post(subir_url, params={"tipo": "ficha"}, files={"archivo": ("ficha.pdf", documento.getvalue(), "application/pdf")}, headers=headers), 201)
            assert comprobar(client.get(f"/api/equipos/{ID_EQUIPO}"), 200)["equipo"]["ficha_pdf_url"] == ficha["url"]
            reemplazo = comprobar(client.post(archivos_url + "/enlace", json={"tipo": "ficha", "url": "https://example.com/ficha.pdf"}, headers=headers), 201)
            assert client.get(ficha["url"]).status_code == 404
            comprobar(client.delete(archivos_url + f"/{reemplazo['id']}", headers=headers), 200)
            assert comprobar(client.get(f"/api/equipos/{ID_EQUIPO}"), 200)["equipo"]["ficha_pdf_url"] is None
            comprobar(client.delete(archivos_url + f"/{foto['id']}", headers=headers), 200)
            comprobar(client.delete(archivos_url + f"/{foto['id']}", headers=headers), 404)
            comprobar(client.get("/api/admin/sesion"), 200)
            comprobar(client.get("/api/admin/equipos"), 200)
            comprobar(client.get("/api/equipos/opciones"), 200)
            comprobar(client.get("/api/comparar/columnas"), 200)
            comprobar(client.get("/api/equipos", params={"q": "Leica", "orden": "peso_asc"}), 200)
            comprobar(client.get("/api/equipos", params={"orden": "invalido"}), 422)
            comprobar(client.get("/api/comparar", params={"ids": ID_EQUIPO}), 422)
            comprobar(client.post("/api/recomendar", json={}), 422)
            comprobar(client.post("/api/recomendar", json={"necesita_imu": False}), 422)
            comprobar(client.post("/api/recomendar", json={"constelaciones_min": 7}), 422)
            comprobar(client.post("/api/recomendar", json={"radio_min_mhz": 450}), 422)
            comprobar(client.patch(
                f"/api/admin/equipos/{ID_EQUIPO}/especificaciones",
                json={"cambios": {"peso_max": -1}}, headers=headers,
            ), 422)
            comprobar(client.patch(
                f"/api/admin/equipos/{ID_EQUIPO}/especificaciones",
                json={"cambios": {"tiene_imu": "Sí"}}, headers=headers,
            ), 422)
            comprobar(client.put(
                f"/api/admin/equipos/{ID_EQUIPO}", json={"descripcion": "Ficha temporal"}, headers=headers,
            ), 200)

            evaluar = comprobar(client.patch(
                f"/api/admin/equipos/{ID_EQUIPO}/especificaciones",
                json={"cambios": {"gps": True, "glonass": True, "ppp_h_cm": 1.2, "tiene_imu": True, "canales_gnss": 500}},
                headers=headers,
            ), 200)
            assert evaluar["constelaciones"] == 2 and evaluar["tiene_ppp"] is True
            rango = comprobar(client.post(
                f"/api/admin/equipos/{ID_EQUIPO}/radio",
                json={"frecuencia_min_mhz": 868, "frecuencia_max_mhz": 868}, headers=headers,
            ), 201)
            assert rango["id_equipo"] == ID_EQUIPO
            comprobar(client.post(
                f"/api/admin/equipos/{ID_EQUIPO}/radio",
                json={"frecuencia_min_mhz": 868, "frecuencia_max_mhz": 868}, headers=headers,
            ), 409)
            comprobar(client.post(
                "/api/admin/equipos/GNSS-INEXISTENTE-TEST/radio",
                json={"frecuencia_min_mhz": 450, "frecuencia_max_mhz": 460}, headers=headers,
            ), 404)
            comprobar(client.put(
                f"/api/admin/equipos/{ID_EQUIPO}/radio/{rango['id']}",
                json={"frecuencia_min_mhz": 900, "frecuencia_max_mhz": 890}, headers=headers,
            ), 422)
            comprobar(client.put(
                f"/api/admin/equipos/{ID_EQUIPO}/radio/{rango['id']}",
                json={"frecuencia_min_mhz": 868, "frecuencia_max_mhz": 868}, headers=headers,
            ), 200)

            comparar = comprobar(client.get(
                "/api/comparar", params={"ids": f"{ID_EQUIPO},GNSS-LEICA-GS18T", "columnas": "tiene_imu,radio_rangos"}
            ), 200)
            assert len(comparar["equipos"]) == 2 and len(comparar["columnas"]) == 2
            ranking = comprobar(client.post(
                "/api/recomendar", json={"top_n": 100, "necesita_imu": True, "radio_min_mhz": 868, "radio_max_mhz": 915}
            ), 200)
            assert ranking["total_equipos"] == total_original + 1
            prueba = next(resultado for resultado in ranking["resultados"] if resultado["equipo"]["id_equipo"] == ID_EQUIPO)
            assert next(item for item in prueba["detalle"] if item["clave"] == "radio_rango")["estado"] == "incumple"
            ranking_canales = comprobar(client.post(
                "/api/recomendar", json={"top_n": 100, "canales_min": 1000}
            ), 200)
            prueba_canales = next(resultado for resultado in ranking_canales["resultados"] if resultado["equipo"]["id_equipo"] == ID_EQUIPO)
            assert prueba_canales["detalle"][0]["estado"] == "incumple"
            assert prueba_canales["detalle"][0]["factor"] == 0.5 and prueba_canales["porcentaje"] == 50

            comprobar(client.put(
                "/api/admin/reglas/tiene_imu", json={"peso": 7, "activo": True}, headers=headers,
            ), 200)
            criterios = comprobar(client.get("/api/recomendador/criterios"), 200)
            assert next(item for item in criterios["criterios"] if item["clave"] == "tiene_imu")["peso"] == 7
            comprobar(client.get("/api/admin/reglas"), 200)
            comprobar(client.put("/api/admin/reglas", json=[
                {"criterio": "tiene_imu", "peso": 7, "activo": False}
            ], headers=headers), 200)
            comprobar(client.post("/api/recomendar", json={"necesita_imu": True}), 422)
            comprobar(client.put("/api/admin/reglas", json=[
                {"criterio": "tiene_imu", "peso": 7, "activo": True}
            ], headers=headers), 200)

            correo = comprobar(client.post(
                "/api/admin/correos", json={"email": f"extra-{USERNAME}@example.com", "contrasena_actual": PASSWORD},
                headers=headers,
            ), 201)
            assert correo["correo"]["verificado_en"] is None
            correo_extra_id = correo["correo"]["id"]
            comprobar(client.get("/api/admin/correos"), 200)
            comprobar(client.put(
                f"/api/admin/correos/{correo_extra_id}/principal",
                json={"contrasena_actual": PASSWORD}, headers=headers,
            ), 404)
            token_verificacion = secrets.token_urlsafe(32)
            with connect() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO admin_email_verification_tokens (recovery_email_id, token_hash, expira_en)
                    VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '24 hours')
                    """,
                    (correo_extra_id, hash_token(token_verificacion)),
                )
            comprobar(client.post("/api/admin/correos/verificar", json={"token": token_verificacion}), 200)
            comprobar(client.put(
                f"/api/admin/correos/{correo_extra_id}/principal",
                json={"contrasena_actual": PASSWORD}, headers=headers,
            ), 200)
            comprobar(client.request("DELETE",
                f"/api/admin/correos/{correo_principal_id}", json={"contrasena_actual": PASSWORD}, headers=headers,
            ), 200)
            comprobar(client.patch(
                f"/api/admin/equipos/{ID_EQUIPO}", json={"publicado": False}, headers=headers,
            ), 200)
            comprobar(client.get(f"/api/equipos/{ID_EQUIPO}"), 404)
            comprobar(client.get(f"/api/admin/equipos/{ID_EQUIPO}"), 200)
            comprobar(client.delete(
                f"/api/admin/equipos/{ID_EQUIPO}/radio/{rango['id']}", headers=headers,
            ), 200)
            comprobar(client.delete(f"/api/admin/equipos/{ID_EQUIPO}", headers=headers), 200)
            comprobar(client.get(f"/api/admin/equipos/{ID_EQUIPO}"), 404)

            token_reset = secrets.token_urlsafe(32)
            nueva_contrasena = secrets.token_urlsafe(24)
            with connect() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO admin_password_reset_tokens (recovery_email_id, token_hash, expira_en)
                    VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '30 minutes')
                    """,
                    (correo_extra_id, hash_token(token_reset)),
                )
            comprobar(client.post(
                "/api/admin/recuperacion/confirmar",
                json={"token": token_reset, "nueva_contrasena": nueva_contrasena, "confirmar_contrasena": "otra" * 4},
            ), 422)
            comprobar(client.post(
                "/api/admin/recuperacion/confirmar",
                json={"token": token_reset, "nueva_contrasena": nueva_contrasena, "confirmar_contrasena": nueva_contrasena},
            ), 200)
            comprobar(client.post(
                "/api/admin/recuperacion/confirmar",
                json={"token": token_reset, "nueva_contrasena": nueva_contrasena, "confirmar_contrasena": nueva_contrasena},
            ), 400)
            comprobar(client.get("/api/admin/equipos"), 401)
            login_nuevo = comprobar(client.post(
                "/api/admin/login", json={"username": USERNAME, "password": nueva_contrasena},
            ), 200)
            contrasena_final = secrets.token_urlsafe(24)
            comprobar(client.put("/api/admin/contrasena", json={
                "contrasena_actual": nueva_contrasena,
                "nueva_contrasena": contrasena_final,
                "confirmar_contrasena": contrasena_final,
            }, headers={"X-CSRF-Token": login_nuevo["csrf_token"]}), 200)
            comprobar(client.get("/api/admin/sesion"), 401)
            login_final = comprobar(client.post("/api/admin/login", json={
                "username": USERNAME, "password": contrasena_final,
            }), 200)
            comprobar(client.post("/api/admin/logout", headers={"X-CSRF-Token": login_final["csrf_token"]}), 200)
            comprobar(client.get("/api/admin/equipos"), 401)
        print("Prueba integrada completa: catálogo, comparador, ranking, sesión, CSRF, escritura y recuperación admin.")
    finally:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT storage_key FROM equipo_archivos WHERE id_equipo=%s", (ID_EQUIPO,))
            archivos = cur.fetchall()
            cur.execute("DELETE FROM equipos WHERE id_equipo = %s", (ID_EQUIPO,))
            if admin_id is not None:
                cur.execute("DELETE FROM admin_users WHERE id = %s", (admin_id,))
            cur.execute("DELETE FROM admin_login_attempts WHERE username = %s", (USERNAME,))
            if regla_original is None:
                cur.execute("DELETE FROM reglas_recomendacion WHERE criterio = 'tiene_imu'")
            else:
                cur.execute(
                    """
                    INSERT INTO reglas_recomendacion (criterio, peso, activo)
                    VALUES (%s, %s, %s) ON CONFLICT (criterio)
                    DO UPDATE SET peso = EXCLUDED.peso, activo = EXCLUDED.activo
                    """,
                    (regla_original["criterio"], regla_original["peso"], regla_original["activo"]),
                )
        for archivo in archivos:
            eliminar_archivo(archivo["storage_key"])


if __name__ == "__main__":
    main()
