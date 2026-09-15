from fastapi import FastAPI

from .routers.equipos import router as equipos_router


app = FastAPI(title="Lici Recomendador API")
app.include_router(equipos_router)
