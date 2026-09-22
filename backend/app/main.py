from fastapi import FastAPI
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .storage import UPLOAD_DIR
from .routers.admin_archivos import router as admin_archivos_router
from .routers.admin_tablas import router as admin_tablas_router

from .routers.equipos import router as equipos_router
from .routers.comparar import router as comparar_router
from .routers.recomendar import router as recomendar_router
from .routers.admin_auth import router as admin_auth_router
from .routers.admin_equipos import router as admin_equipos_router
from .routers.admin_reglas import router as admin_reglas_router
from .routers.admin_recuperacion import router as admin_recuperacion_router
from .routers.admin_correos import router as admin_correos_router
from .routers.ia import router as ia_router
from .migrations import apply_runtime_migrations


app = FastAPI(title="Licitex API")


@app.on_event("startup")
def migrate_production_database():
    apply_runtime_migrations()
from .routers.admin_almacenamiento import router as admin_almacenamiento_router
app.include_router(admin_almacenamiento_router)
from .routers.controladoras import router as controladoras_router
app.include_router(controladoras_router)
if not os.getenv("VERCEL") and os.getenv("MEDIA_STORAGE", "local") == "local":
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/archivos", StaticFiles(directory=UPLOAD_DIR), name="archivos")
app.include_router(admin_archivos_router)
app.include_router(admin_tablas_router)
app.include_router(equipos_router)
app.include_router(comparar_router)
app.include_router(recomendar_router)
app.include_router(admin_auth_router)
app.include_router(admin_equipos_router)
app.include_router(admin_reglas_router)
app.include_router(admin_recuperacion_router)
app.include_router(admin_correos_router)
app.include_router(ia_router)

# Registrar después de la API para conservar todas sus rutas. También permite
# servir /index.html cuando un rewrite SPA llega a la función Python.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "public"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
