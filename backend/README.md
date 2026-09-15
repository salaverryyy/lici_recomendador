# Primer endpoint del catálogo

Desde `backend`:

1. Crear el entorno: `python -m venv .venv`
2. Instalar: `.venv\\Scripts\\python.exe -m pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y escribir la contraseña local de PostgreSQL en `DB_PASSWORD`. `.env` está ignorado por Git.
4. Iniciar: `.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload`
5. Abrir `http://127.0.0.1:8000/api/equipos`. Deben aparecer los 22 equipos publicados.

`http://127.0.0.1:8000/docs` muestra la documentación interactiva de FastAPI.
