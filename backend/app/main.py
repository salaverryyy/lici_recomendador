from fastapi import FastAPI

from .routers.equipos import router as equipos_router
from .routers.comparar import router as comparar_router
from .routers.recomendar import router as recomendar_router
from .routers.admin_auth import router as admin_auth_router
from .routers.admin_equipos import router as admin_equipos_router
from .routers.admin_reglas import router as admin_reglas_router
from .routers.admin_recuperacion import router as admin_recuperacion_router
from .routers.admin_correos import router as admin_correos_router


app = FastAPI(title="Lici Recomendador API")
app.include_router(equipos_router)
app.include_router(comparar_router)
app.include_router(recomendar_router)
app.include_router(admin_auth_router)
app.include_router(admin_equipos_router)
app.include_router(admin_reglas_router)
app.include_router(admin_recuperacion_router)
app.include_router(admin_correos_router)
