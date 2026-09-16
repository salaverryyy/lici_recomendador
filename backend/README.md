# Primer endpoint del catálogo

Desde `backend`:

1. Crear el entorno: `python -m venv .venv`
2. Instalar: `.venv\\Scripts\\python.exe -m pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y escribir la contraseña local de PostgreSQL en `DB_PASSWORD`. `.env` está ignorado por Git.
4. Iniciar: `.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload`
5. Abrir `http://127.0.0.1:8000/api/equipos`. Deben aparecer los 22 equipos publicados.

`http://127.0.0.1:8000/docs` muestra la documentación interactiva de FastAPI.

## Licitex y archivos

Instalar nuevamente los requisitos si el entorno es anterior a la galería. Aplicar el esquema
`sql/07_archivos_equipos.sql` a nuevas bases; ya está aplicado en la base local de desarrollo.
Las fotos y fichas cargadas localmente se conservan en `backend/uploads/` (fuera de Git).
Ver `docs/archivos_equipos.md` para configurar almacenamiento persistente en producción.
El acceso y la creación del administrador se describen en `docs/api_acceso.md`.
