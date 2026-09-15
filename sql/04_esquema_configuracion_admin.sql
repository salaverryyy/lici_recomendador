-- Tablas de configuracion y administracion. No insertar usuarios ni pesos todavia.

CREATE TABLE reglas_recomendacion (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    criterio TEXT NOT NULL UNIQUE,
    peso NUMERIC(8,2) NOT NULL CHECK (peso >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE admin_users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON COLUMN reglas_recomendacion.peso IS
    'Peso relativo editable. El backend normalizara los pesos activos al calcular porcentajes.';
COMMENT ON COLUMN admin_users.password_hash IS
    'Hash de contrasena generado por el backend con un algoritmo adaptativo; nunca texto plano.';

-- Resultado esperado: las dos tablas creadas y vacias.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('reglas_recomendacion', 'admin_users')
ORDER BY table_name;
