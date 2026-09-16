# Arquitectura y despliegue propuestos

## Estructura

Un repositorio con `frontend/` (React, TypeScript y Vite) y `backend/` (FastAPI).
La API se organiza por módulos de catálogo, recomendación y administración cuando se construyan.
Los datos y reglas se guardan en un PostgreSQL independiente. No se crean microservicios por criterio:
el catálogo y el ranking comparten datos y cambian juntos en este MVP.

## Vercel

Preparar dos proyectos Vercel conectados al mismo repositorio:

1. Proyecto web con directorio raíz `frontend/`.
2. Proyecto API con directorio raíz `backend/`; `server.py` exporta la instancia FastAPI `app`.

Cada proyecto obtiene inicialmente una URL `*.vercel.app`. Un dominio propio permite usar,
por ejemplo, `ejemplo.com` para la web y `api.ejemplo.com` para la API. Los nombres de ejemplo
no son dominios reservados ni registrados. El dominio requiere registro y renovación;
los proyectos y la base de datos requieren cuentas activas y cumplir el plan contratado.
FastAPI en Vercel funciona como una Function: no hay un proceso Python encendido continuamente.

`localhost:5432` solo sirve en desarrollo. Antes de desplegar, migrar el esquema y los datos a
un PostgreSQL alojado (por ejemplo, una integración Postgres del Marketplace), configurar en
el proyecto API una `DATABASE_URL` segura de producción y utilizar la conexión agrupada/pooled
del proveedor si está disponible. Nunca publicar contraseñas ni URL de conexión en Git.

El proyecto web podrá llamar a la API por su dominio o mediante un proxy `/api` en el dominio
principal; elegiremos la ruta al construir el frontend para evitar cambios innecesarios de CORS.

No se ha desplegado ningún proyecto ni migrado la base de datos. La base local `interfaz_lici`
es la fuente actual del catálogo.

## Orden de trabajo

Probar primero frontend y backend juntos localmente. Después configurar PostgreSQL alojado,
almacenamiento persistente de archivos, SMTP, proxy de API y cookies seguras en un entorno de
prueba. Repetir la verificación antes de publicar. Ver `archivos_equipos.md` para almacenamiento
y límites de carga; el visor 3D queda para una etapa posterior.
