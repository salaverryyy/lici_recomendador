# Licitex — frontend local

React, TypeScript y Vite. El diseño parte del PDF de Figma, adaptado a los datos y criterios reales.

Desde `frontend`:

```powershell
npm install
npm run dev
```

Abrir la dirección que imprime Vite (normalmente http://127.0.0.1:5173).
El backend debe estar encendido en http://127.0.0.1:8000. Vite redirige `/api` y `/archivos`
al backend para mantener las cookies de sesión en el mismo origen. Si el backend usa otro puerto,
definir `API_PROXY_TARGET` antes de iniciar Vite.

`npm run build` verifica TypeScript y produce `dist/`.
Para publicar, configurar reescrituras de `/api/*` hacia la API y, si corresponde, `/archivos/*`.
Las demás rutas deben resolver a `index.html`. No definir secretos en variables `VITE_*`.

Incluye catálogo, detalle con galería, comparador con selección de características,
recomendador, administración del catálogo/especificaciones/radios/archivos/pesos,
gestión de correos y cambio/recuperación de contraseña. Los correos requieren configurar SMTP
en el backend. El modelo 3D es un enlace opcional; aún no hay visor interactivo.

No se inventan imágenes ni especificaciones: se muestran los archivos y datos disponibles.
