# Acceso a la API

Los endpoints de lectura del catálogo y de recomendación son públicos: sirven al visitante de
la interfaz sin cuenta. La lista `/api/equipos` y el detalle `/api/equipos/{id_equipo}` exponen
solo equipos con `publicado = TRUE`.

Los endpoints para crear, editar, ocultar o borrar equipos, cambiar pesos y administrar correos
de recuperación requieren una sesión de administrador y `X-CSRF-Token` para cada escritura.
No basta con ocultar botones en React. El login, la solicitud de recuperación y la confirmación
por token son públicos; la solicitud de recuperación responde sin revelar si una dirección existe.

El proveedor de correo todavía no está conectado: los envíos devuelven 503 y las direcciones
nuevas permanecen sin verificar hasta confirmar un enlace real. La cuenta inicial se crea desde
terminal, sin endpoint público de registro.
