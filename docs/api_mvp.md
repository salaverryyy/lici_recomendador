# Endpoints del MVP

## Públicos, sin cuenta

| Método | Ruta | Uso en la interfaz |
| --- | --- | --- |
| GET | `/api/equipos` | Lista, búsqueda `q`, filtros `marca`/`categoria` y orden `marca`/`modelo`/`anio_desc`/`canales_desc`/`peso_asc` |
| GET | `/api/equipos/opciones` | Marcas y categorías existentes para selectores |
| GET | `/api/equipos/{id_equipo}` | Ficha, especificaciones y rangos de radio de un equipo publicado |
| GET | `/api/comparar/columnas` | Columnas disponibles para encender o apagar en el comparador |
| GET | `/api/comparar?ids=A,B&columnas=tiene_imu,peso_max` | Comparación de 2 o más equipos publicados, en el orden pedido |
| GET | `/api/recomendador/criterios` | Nombres, unidades, pesos y estado de los criterios del formulario |
| POST | `/api/recomendar` | Ranking explicado con `top_n` elegible; cuenta todos los publicados |

`POST /api/recomendar` recibe solo los campos seleccionados. Ejemplo:

```json
{
  "top_n": 11,
  "necesita_imu": true,
  "canales_min": 1000,
  "radio_min_mhz": 450,
  "radio_max_mhz": 460
}
```

Un booleano en `false` significa «no lo necesito» y no participa. Dejar cualquier campo fuera también
lo omite. Los equipos que fallan permanecen en el ranking; cada criterio tiene estado `cumple`,
`incumple` o `sin_datos`, con valor real y pedido. Un valor numérico cercano al umbral recibe
puntos parciales aunque siga marcado como incumplimiento; funciones booleanas y radio son binarias.
`top_n` admite 1 a 100 y muestra hasta el total
disponible. El porcentaje se divide entre la suma de pesos seleccionados, nunca entre un total fijo.

La radio se evalúa como cobertura de un único rango real; dos puntos 868 y 915 no cubren el tramo
continuo 868–915. `constelaciones_min` admite 1 a 6 porque SBAS no participa en esa suma.
Los pesos cargados por defecto en el código son provisionales y el admin podrá modificarlos.

## Administrador

| Método | Ruta | Uso |
| --- | --- | --- |
| POST | `/api/admin/login` | Contraseña y sesión en cookie HttpOnly |
| GET | `/api/admin/sesion` | Identidad y token CSRF de la sesión vigente |
| POST | `/api/admin/logout` | Revocar sesión |
| PUT | `/api/admin/contrasena` | Cambiar contraseña, confirmándola dos veces |
| GET | `/api/admin/equipos` | Lista completa, incluidos no publicados |
| GET | `/api/admin/equipos/{id_equipo}` | Datos para editar |
| POST | `/api/admin/equipos` | Crear equipo |
| PATCH/PUT | `/api/admin/equipos/{id_equipo}` | Editar datos generales y `publicado` |
| DELETE | `/api/admin/equipos/{id_equipo}` | Eliminar equipo y datos relacionados |
| PATCH | `/api/admin/equipos/{id_equipo}/especificaciones` | Editar campos técnicos; recalcula `constelaciones` y `tiene_ppp` |
| POST | `/api/admin/equipos/{id_equipo}/radio` | Agregar rango de radio |
| PUT/DELETE | `/api/admin/equipos/{id_equipo}/radio/{radio_id}` | Editar/eliminar rango |
| GET | `/api/admin/reglas` | Ver pesos efectivos |
| PUT | `/api/admin/reglas` | Cambiar varias reglas en una transacción |
| PUT | `/api/admin/reglas/{criterio}` | Cambiar un peso o activar/desactivar un criterio |
| GET/POST | `/api/admin/correos` | Ver/agregar correos de recuperación |
| POST | `/api/admin/correos/{correo_id}/enviar-verificacion` | Enviar enlace de verificación |
| POST | `/api/admin/correos/verificar` | Confirmar un nuevo correo con token |
| PUT | `/api/admin/correos/{correo_id}/principal` | Cambiar correo principal, previa contraseña |
| DELETE | `/api/admin/correos/{correo_id}` | Desactivar correo secundario, previa contraseña |
| POST | `/api/admin/recuperacion/solicitar` | Solicitar enlace con respuesta genérica |
| POST | `/api/admin/recuperacion/confirmar` | Token de un solo uso y nueva contraseña escrita dos veces |

Las rutas de lectura administrativa exigen sesión. Las escrituras exigen además `X-CSRF-Token`.
La creación inicial del administrador se hace desde terminal con `python -m app.create_admin`:
no existe un endpoint público de registro. El primer correo queda sin verificar. Los endpoints
de envío devuelven 503 hasta conectar un proveedor SMTP; no se enviará ni se considerará válido
un enlace de recuperación durante esa etapa. La confirmación con token ya está implementada.

## Pendiente antes de producción

Configurar el correo SMTP y verificar la dirección principal, migrar PostgreSQL local a un
proveedor alojado, configurar el dominio y una ruta `/api` del frontend hacia la API.
El login y los correos se probaron con datos temporales; no se ha creado un administrador real.
