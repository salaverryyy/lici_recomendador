# Fotos y fichas de Licitex

Aplicar `sql/07_archivos_equipos.sql` después de los esquemas existentes. Ya se aplicó a la base
local durante la implementación. La migración conserva las URLs actuales y puede repetirse.

Cada equipo admite hasta 20 fotografías. La portada continúa en `equipos.imagen_url`, por lo
que catálogo y ranking mantienen su contrato. El detalle público añade `fotografias` con
ID, URL, descripción accesible y orden. La ficha vigente continúa en `ficha_pdf_url`.
Los modelos 3D mantienen el campo opcional `modelo_3d_url` existente; se añade desde edición
general. Su carga y visor quedan para una etapa posterior.

## Administración

Todos estos endpoints requieren sesión; los cambios también `X-CSRF-Token`:

- `GET /api/admin/equipos/{id}/archivos`: lista.
- `POST .../archivos/enlace`: URL HTTP(S), `tipo` (`foto` o `ficha`), texto alternativo y orden opcionales.
- `POST .../archivos/subir?tipo=foto|ficha`: archivo multipart en campo `archivo`.
- `PATCH .../archivos/{archivo_id}`: texto alternativo/orden de una foto.
- `PUT .../archivos/{archivo_id}/portada`: selecciona la portada.
- `DELETE .../archivos/{archivo_id}`: elimina una foto o ficha; al quitar la portada se elige la siguiente.

Subir una ficha reemplaza la anterior. Se comprueba el contenido, no solo la extensión:
fotos JPG/PNG/WebP hasta 5 MB, PDF sin contraseña y con páginas hasta 20 MB en local.
En Vercel esta carga mediante API se limita a 3 MB, dejando margen al multipart dentro del límite
de 4,5 MB de la plataforma. Para archivos mayores hace falta integrar cargas directas firmadas
al almacenamiento antes del despliegue. No hay carga directa implementada aún.
Referencia: https://vercel.com/docs/functions/limitations

## Persistencia

Desarrollo usa `MEDIA_STORAGE=local`, carpeta ignorada `backend/uploads`, servida por `/archivos`.
Producción puede usar almacenamiento compatible S3 con:

```
MEDIA_STORAGE=s3
S3_BUCKET=...
S3_ENDPOINT_URL=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=auto
MEDIA_PUBLIC_URL=https://archivos.ejemplo.com
```

Guardar las credenciales exclusivamente en `.env` o configuración del proveedor.
El bucket necesita permitir lectura pública mediante la URL elegida, y las credenciales de la API
necesitan acceso a escritura/eliminación en el prefijo `equipos/`. No se usa ACL pública por objeto.
En Vercel se rechaza el modo local. La conexión S3 está preparada pero no se ha probado con un
proveedor real. Nunca se descargan ni se borran URLs externas desde la API.

Los archivos gestionados se borran al reemplazar ficha, quitar un archivo o eliminar su equipo
mediante la API. Si falla la limpieza externa se registra el error para reconciliar objetos huérfanos;
los registros del catálogo quedan eliminados. Eliminar directamente en SQL no limpia los objetos.
Las fotos y fichas son material público: ocultar un equipo lo saca del catálogo, pero no convierte
sus URLs en enlaces privados.
