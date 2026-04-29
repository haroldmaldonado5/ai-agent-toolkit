-- Tabla de errores de publicación
CREATE TABLE IF NOT EXISTS errores_publicacion (
    id SERIAL PRIMARY KEY,
    publicacion_id INTEGER,
    plataforma VARCHAR(50) NOT NULL,
    error TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resuelto BOOLEAN DEFAULT FALSE
);

-- Tabla para tokens de APIs
CREATE TABLE IF NOT EXISTS api_tokens (
    id SERIAL PRIMARY KEY,
    plataforma VARCHAR(50) UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    account_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de aprobaciones
CREATE TABLE IF NOT EXISTS aprobaciones (
    id SERIAL PRIMARY KEY,
    publicacion_id INTEGER,
    solicitado_por VARCHAR(255),
    aprobado_por VARCHAR(255),
    estado VARCHAR(50) DEFAULT 'pendiente',
    razon_rechazo TEXT,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_decision TIMESTAMP
);

-- Tabla de multimedia
CREATE TABLE IF NOT EXISTS multimedia (
    id SERIAL PRIMARY KEY,
    publicacion_id INTEGER,
    tipo VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    url_local TEXT,
    orden INTEGER DEFAULT 1,
    dimensiones VARCHAR(50),
    duracion INTEGER,
    tamano_bytes BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs
CREATE TABLE IF NOT EXISTS logs_publicacion (
    id SERIAL PRIMARY KEY,
    publicacion_id INTEGER,
    plataforma VARCHAR(50) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    mensaje TEXT,
    response_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);