# Publicación de Licitex

Configuración preparada para UN proyecto Vercel con raíz `./`, framework FastAPI.
`server.py` exporta la API; `requirements.txt` instala dependencias. El build de
`vercel.json` compila React y copia a `public/` para el CDN. Los rewrites cubren
rutas React; `/api` y `/docs` permanecen en FastAPI. Mismo origen para cookies.
Falta validar esta configuración en un despliegue real.

## Opciones y límites

Vercel Hobby es gratuito para uso personal no comercial. No garantiza alojamiento
comercial gratuito: [condiciones](https://vercel.com/docs/plans/hobby).
Neon Free permite PostgreSQL externo sujeto a cuotas:
[cuotas](https://github.com/neondatabase/website/blob/main/content/faqs/free-plan-limits-and-quotas.md).
Cloudflare R2 ofrece almacenamiento S3 con cuotas gratuitas y cobro de excedentes:
[precios](https://developers.cloudflare.com/r2/pricing/).
Render es alternativa para FastAPI, pero su servicio gratuito duerme tras 15 minutos
sin tráfico: [límites](https://render.com/docs/free).
[FastAPI y archivos public/ en Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

## Pasos

1. Crear PostgreSQL alojado. En pgAdmin hacer Backup local en formato Custom con
   esquema y datos y restaurar en la base remota VACÍA, sin owners/privilegios
   locales. El backup incluye hashes y cuentas: conservar privado fuera de Git.
   Incluye las migraciones ya aplicadas; no repetir cargas iniciales sobre la copia.
   Aplicar SQL 13 si falta. Cerrar sesiones admin heredadas antes de publicar.
2. Crear bucket S3/R2 con acceso público a objetos y configurar variables abajo.
   PDFs/fotos no viajan en el backup. Volver a subir las 23 fichas desde admin tras
   publicar; las URLs locales `/archivos/` no funcionarán en producción. Comprobar
   fichas y portadas antes de dar el sitio por terminado. Conservar originales.
3. Importar repositorio en Vercel, raíz `./`, mantener build de vercel.json.
4. Probar HTTPS: catálogo, rutas profundas, login/sesión, edición con CSRF,
   ranking y empates, ampliación de memoria, comparación, carga/borrado de PDF.
   Para escrituras usar equipo temporal y eliminarlo al terminar.
5. Configurar SMTP, verificar correo del admin y probar recuperación real.
   Sin SMTP la recuperación responde 503 y no está habilitada.

## Variables privadas del servidor

`DATABASE_URL`: PostgreSQL remoto con SSL, preferiblemente endpoint pooled.
`MEDIA_STORAGE=s3`, `S3_BUCKET`, `S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=auto`, `MEDIA_PUBLIC_URL`.
`FRONTEND_URL=https://nombre.vercel.app` (o dominio propio).
`SMTP_HOST`, `SMTP_PORT=587` o `465`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`.
Vercel proporciona `VERCEL`, que activa cookies Secure y almacenamiento persistente.
Nunca publicar `.env` ni poner estas credenciales en variables VITE del frontend.

La URL del proyecto evita comprar un dominio inicialmente. El dominio propio tiene
costes independientes. La app limita cargas a 3 MB en Vercel. El modelo 3D conserva
URL; carga y visor quedan pendientes. No existe garantía de gratuidad permanente.

Preparado no significa publicado: faltan cuentas, conexión remota, migración de
archivos y comprobación HTTPS real.
