# Primer endpoint del catálogo

Desde `backend`:

1. Crear el entorno: `python -m venv .venv`
2. Instalar: `.venv\\Scripts\\python.exe -m pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y escribir la contraseña local de PostgreSQL en `DB_PASSWORD`. `.env` está ignorado por Git.
4. Iniciar: `.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload`
5. Abrir `http://127.0.0.1:8000/api/equipos`. Deben aparecer los equipos publicados.

`http://127.0.0.1:8000/docs` muestra la documentación interactiva de FastAPI.

## Licitex y archivos

Instalar nuevamente los requisitos si el entorno es anterior a la galería. Aplicar el esquema
`sql/07_archivos_equipos.sql` a nuevas bases; ya está aplicado en la base local de desarrollo.
Las fotos y fichas cargadas localmente se conservan en `backend/uploads/` (fuera de Git).
Ver `docs/archivos_equipos.md` para configurar almacenamiento persistente en producción.
El acceso y la creación del administrador se describen en `docs/api_acceso.md`.

## Asistente con IA

El asistente convierte texto libre en los mismos requisitos validados que usan los
rankings de GNSS, controladoras y escáneres SLAM. La IA no puntúa equipos ni escribe datos en la BD.

Para probarlo localmente, crear una clave de Gemini en Google AI Studio y agregar a
`backend/.env`:

```env
GEMINI_API_KEY=TU_CLAVE
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite
```

La clave permanece en el backend. `GET /api/ia/estado` indica si el servicio está
configurado o si la cuota gratuita se agotó. Los últimos cinco chats se guardan en
`localStorage` del navegador y no se comparten con otros visitantes. Cada respuesta
usa como memoria un máximo de seis turnos anteriores del chat activo. El backend
recupera de PostgreSQL las fichas técnicas más relacionadas con la conversación
(RAG léxico local, sin embeddings ni un servicio vectorial adicional).
Licitex no impone un límite propio de consultas. Si el modelo principal agota su
cuota o queda temporalmente indisponible, prueba los modelos de respaldo configurados
antes de mostrar el código de error devuelto por Gemini.

Las respuestas se solicitan con un esquema JSON y se leen todos los fragmentos
de texto de salida. Si Gemini trunca una respuesta, se reintenta con mayor
presupuesto de salida; si sigue siendo inválida, se prueban los respaldos y se
informa un error 502 sin bloquear globalmente la IA. El porcentaje de ranking
solo cubre los criterios evaluados; los requisitos no evaluables se conservan
para revisión manual. Cuando se exige memoria interna instalada, la IA envía
`memoria_solo_fabrica=true` para que una ampliación no cubra ese mínimo.
