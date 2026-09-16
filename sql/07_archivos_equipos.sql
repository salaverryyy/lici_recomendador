-- Galería de fotos y ficha técnica; conserva las URLs actuales del catálogo.
BEGIN;
CREATE TABLE IF NOT EXISTS equipo_archivos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_equipo TEXT NOT NULL REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('foto', 'ficha')),
    url TEXT NOT NULL,
    texto_alternativo TEXT NOT NULL DEFAULT '',
    orden INTEGER NOT NULL DEFAULT 0 CHECK (orden >= 0),
    storage_key TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS equipo_archivos_equipo ON equipo_archivos(id_equipo, tipo, orden, id);
CREATE UNIQUE INDEX IF NOT EXISTS equipo_una_ficha ON equipo_archivos(id_equipo) WHERE tipo = 'ficha';
INSERT INTO equipo_archivos(id_equipo, tipo, url, texto_alternativo)
SELECT e.id_equipo, 'foto', e.imagen_url, e.marca || ' ' || e.modelo
FROM equipos e WHERE e.imagen_url IS NOT NULL AND NOT EXISTS
(SELECT 1 FROM equipo_archivos a WHERE a.id_equipo = e.id_equipo AND a.tipo = 'foto' AND a.url = e.imagen_url);
INSERT INTO equipo_archivos(id_equipo, tipo, url)
SELECT e.id_equipo, 'ficha', e.ficha_pdf_url FROM equipos e
WHERE e.ficha_pdf_url IS NOT NULL AND NOT EXISTS
(SELECT 1 FROM equipo_archivos a WHERE a.id_equipo = e.id_equipo AND a.tipo = 'ficha');
COMMIT;
