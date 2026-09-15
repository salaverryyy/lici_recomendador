-- Ejecutar una vez en interfaz_lici después de 04 y 05.
-- Sesiones y verificación de nuevos correos del administrador.

CREATE TABLE admin_sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    admin_user_id BIGINT NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    csrf_token TEXT NOT NULL,
    expira_en TIMESTAMPTZ NOT NULL,
    revocado_en TIMESTAMPTZ,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX admin_sessions_usuario_vigencia
    ON admin_sessions (admin_user_id, expira_en)
    WHERE revocado_en IS NULL;

CREATE TABLE admin_login_attempts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL,
    exitoso BOOLEAN NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX admin_login_attempts_nombre_fecha
    ON admin_login_attempts (username, creado_en DESC);

CREATE TABLE admin_email_verification_tokens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recovery_email_id BIGINT NOT NULL REFERENCES admin_recovery_emails(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expira_en TIMESTAMPTZ NOT NULL,
    usado_en TIMESTAMPTZ,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('admin_sessions', 'admin_login_attempts', 'admin_email_verification_tokens')
ORDER BY table_name;
