-- Estructura para recuperar la contrasena del administrador.
-- El correo principal se registrara y verificara cuando configuremos el backend.

CREATE TABLE admin_recovery_emails (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_user_id BIGINT NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    es_principal BOOLEAN NOT NULL DEFAULT FALSE,
    verificado_en TIMESTAMPTZ,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT admin_recovery_email_unico UNIQUE (admin_user_id, email)
);

CREATE UNIQUE INDEX admin_recovery_principal_unico
    ON admin_recovery_emails (admin_user_id)
    WHERE es_principal AND activo;

CREATE TABLE admin_password_reset_tokens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recovery_email_id BIGINT NOT NULL REFERENCES admin_recovery_emails(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expira_en TIMESTAMPTZ NOT NULL,
    usado_en TIMESTAMPTZ,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN admin_recovery_emails.verificado_en IS
    'Enviar enlaces de recuperacion solo a correos verificados y activos.';
COMMENT ON COLUMN admin_password_reset_tokens.token_hash IS
    'Hash del token aleatorio; el token enviado por correo nunca se guarda en texto plano.';

-- Resultado esperado: las dos tablas de recuperacion.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('admin_recovery_emails', 'admin_password_reset_tokens')
ORDER BY table_name;
