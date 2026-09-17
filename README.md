# Licitex

Catálogo técnico, comparador y recomendador de equipos. Inicialmente GNSS, con categorías
preparadas para ampliar el catálogo. React/TypeScript/Vite, FastAPI y PostgreSQL.

## Probar localmente

Backend (terminal en `backend`):

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend (otra terminal en `frontend`):

```powershell
npm install
npm run dev
```

Abrir http://127.0.0.1:5173. La API y sus documentos están en http://127.0.0.1:8000/docs.
La base local debe tener los esquemas `sql/01` a `sql/09` aplicados. No volver a importar los
CSV si ya están cargados. Ver `docs/api_acceso.md` para crear el administrador.

Las modificaciones del catálogo requieren sesión de administrador y protección CSRF.
Ver `docs/archivos_equipos.md` para fotos y PDFs, y `docs/arquitectura_despliegue.md` para producción.
El envío de correos y el almacenamiento S3 necesitan configuración externa. El visor 3D queda pendiente.
