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

## Asistente con IA

El asistente convierte texto libre en los mismos requisitos validados que usan los
rankings de GNSS y controladoras. La IA no puntúa equipos ni escribe datos en la BD.

Para probarlo localmente, crear una clave de Gemini en Google AI Studio y agregar a
`backend/.env`:

```env
GEMINI_API_KEY=TU_CLAVE
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-3.8-flash
```

La clave permanece en el backend. `GET /api/ia/estado` indica si el servicio está
configurado o si la cuota gratuita se agotó. Los últimos cinco chats se guardan en
`localStorage` del navegador y no se comparten con otros visitantes.
