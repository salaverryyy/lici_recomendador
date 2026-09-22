-- Esquema del catalogo GNSS. Ejecutar en una base de datos vacia.
-- Los archivos CSV preparados usan el mismo orden de columnas de estas tablas.

CREATE TABLE equipos (
    id_equipo TEXT PRIMARY KEY,
    marca TEXT NOT NULL,
    modelo TEXT NOT NULL,
    categoria TEXT NOT NULL,
    descripcion TEXT,
    anio_modelo INTEGER,
    imagen_url TEXT,
    modelo_3d_url TEXT,
    ficha_pdf_url TEXT,
    web_url TEXT,
    publicado BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE base_evaluacion (
    id_equipo TEXT PRIMARY KEY REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    tiene_imu BOOLEAN,
    tiene_camara BOOLEAN,
    canales_gnss INTEGER CHECK (canales_gnss >= 0),
    memoria NUMERIC(10,3) CHECK (memoria >= 0),
    sim_4g BOOLEAN,
    laser BOOLEAN,
    laser_alcance_m NUMERIC(8,2) CHECK (laser_alcance_m >= 0),
    bateria_intercambiable BOOLEAN,
    bateria_caliente BOOLEAN,
    mp_camara NUMERIC(6,1) CHECK (mp_camara >= 0),
    radio_frecuencia TEXT,
    constelaciones INTEGER CHECK (constelaciones >= 0),
    autonomia_bateria NUMERIC(6,1) CHECK (autonomia_bateria >= 0),
    peso_max INTEGER CHECK (peso_max >= 0),
    tiempo_inicializacion INTEGER CHECK (tiempo_inicializacion >= 0),
    rtk_horizontal_mm NUMERIC(8,2),
    rtk_vertical_mm NUMERIC(8,2),
    rtk_ppm_h NUMERIC(8,2),
    rtk_ppm_v NUMERIC(8,2),
    static_horizontal_mm NUMERIC(8,2),
    static_vertical_mm NUMERIC(8,2),
    static_ppm_h NUMERIC(8,2),
    static_ppm_v NUMERIC(8,2),
    largo_mm NUMERIC(8,1),
    ancho_mm NUMERIC(8,1),
    alto_mm NUMERIC(8,1),
    gps BOOLEAN,
    glonass BOOLEAN,
    galileo BOOLEAN,
    beidou BOOLEAN,
    qzss BOOLEAN,
    navic_irnss BOOLEAN,
    sbas BOOLEAN,
    tiene_ppp BOOLEAN,
    ppp_h_cm NUMERIC(8,1),
    ppp_v_cm NUMERIC(8,1)
);

CREATE TABLE equipo_radio_frecuencia (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_equipo TEXT NOT NULL REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    frecuencia_min_mhz NUMERIC(8,3) NOT NULL CHECK (frecuencia_min_mhz >= 0),
    frecuencia_max_mhz NUMERIC(8,3) NOT NULL CHECK (frecuencia_max_mhz >= 0),
    CONSTRAINT radio_rango_valido CHECK (frecuencia_min_mhz <= frecuencia_max_mhz),
    CONSTRAINT radio_rango_unico UNIQUE (id_equipo, frecuencia_min_mhz, frecuencia_max_mhz)
);

COMMENT ON COLUMN base_evaluacion.memoria IS 'Capacidad de almacenamiento en GB decimales; 0.056 GB = 56 MB.';
COMMENT ON COLUMN base_evaluacion.autonomia_bateria IS 'Horas.';
COMMENT ON COLUMN base_evaluacion.peso_max IS 'Peso real del equipo en gramos; el maximo permitido es un filtro de consulta.';
COMMENT ON COLUMN base_evaluacion.tiempo_inicializacion IS 'Segundos desde el encendido hasta que el equipo termina de iniciar; no incluye RTK.';
COMMENT ON COLUMN base_evaluacion.constelaciones IS 'Suma de GPS, GLONASS, GALILEO, BEIDOU, QZSS y NAVIC_IRNSS. SBAS se excluye.';
COMMENT ON COLUMN base_evaluacion.tiene_ppp IS 'TRUE si hay al menos una precision PPP; FALSE si ambos campos PPP son NULL, segun confirmacion de los datos.';
COMMENT ON COLUMN base_evaluacion.ppp_h_cm IS 'Precision PPP horizontal en centimetros.';
COMMENT ON COLUMN base_evaluacion.ppp_v_cm IS 'Precision PPP vertical en centimetros.';

-- Resultado esperado: equipos, base_evaluacion y equipo_radio_frecuencia.
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('equipos', 'base_evaluacion', 'equipo_radio_frecuencia')
ORDER BY table_name;
