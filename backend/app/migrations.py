"""Migraciones idempotentes necesarias para despliegues serverless."""

import os
from pathlib import Path

from psycopg import Error as DatabaseError

from .db import connect


def apply_runtime_migrations() -> None:
    if not os.getenv("VERCEL"):
        return
    versions = (
        "20_sinognss_t20",
        "21_slam_scanners",
        "22_sinognss_r80",
        "23_sc260_visibility",
        "24_ia_provider_limits",
        "25_auditoria_integral",
        "26_software_procesamiento",
        "27_software_auditoria",
        "28_condiciones_sim",
    )
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(hashtext('licitex_runtime_migrations'))")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS esquema_migraciones (
                    version TEXT PRIMARY KEY,
                    aplicada_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            for version in versions:
                cur.execute("SELECT 1 FROM esquema_migraciones WHERE version=%s", (version,))
                if cur.fetchone():
                    continue
                path = Path(__file__).resolve().parents[2] / "sql" / f"{version}.sql"
                script = path.read_text(encoding="utf-8").strip()
                if script.startswith("BEGIN;"):
                    script = script[len("BEGIN;"):].lstrip()
                if script.endswith("COMMIT;"):
                    script = script[:-len("COMMIT;")].rstrip()
                cur.execute(script)
                cur.execute("INSERT INTO esquema_migraciones(version) VALUES(%s)", (version,))
    except (OSError, DatabaseError) as exc:
        # La API conserva disponibilidad para permitir diagnóstico desde Admin.
        print(f"No se pudieron aplicar las migraciones de catálogo: {type(exc).__name__}")
