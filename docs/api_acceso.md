# Acceso a la API

Los endpoints de lectura del catálogo y de recomendación son públicos: sirven al visitante de
la interfaz sin cuenta. La lista `/api/equipos` y el detalle `/api/equipos/{id_equipo}` exponen
solo equipos con `publicado = TRUE`.

Cuando se implementen, los endpoints para crear, editar, ocultar o borrar equipos, cambiar
pesos y administrar correos de recuperación requerirán autenticación de administrador y
verificación de permisos en el backend en cada petición. No basta con ocultar botones en React.
La recuperación de contraseña tendrá una ruta pública para solicitarla, con respuestas que no
revelen si una dirección existe y controles de abuso.

Todavía no hay endpoints de escritura ni login de administrador; por eso no hay operaciones de
modificación expuestas sin protección.
