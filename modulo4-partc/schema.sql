CREATE TABLE IF NOT EXISTS metricas_posts (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(255) NOT NULL,
    plataforma VARCHAR(50) NOT NULL CHECK (plataforma IN ('instagram', 'twitter', 'linkedin', 'tiktok', 'youtube')),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    vistas INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comentarios INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, plataforma, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_metricas_plataforma ON metricas_posts(plataforma);
CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas_posts(timestamp DESC);

CREATE TABLE IF NOT EXISTS reportes_programados (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    frecuencia VARCHAR(50) NOT NULL CHECK (frecuencia IN ('diario', 'semanal', 'mensual', 'manual')),
    dia_semana INTEGER CHECK (dia_semana BETWEEN 0 AND 6),
    hora_ejecucion TIME,
    plataformas TEXT[] DEFAULT ARRAY['instagram', 'twitter', 'linkedin', 'tiktok', 'youtube'],
    metricas_incluidas TEXT[] DEFAULT ARRAY['vistas', 'likes', 'comentarios', 'shares', 'engagement_rate'],
    formato VARCHAR(10) NOT NULL CHECK (formato IN ('pdf', 'csv', 'excel')),
    email_destino VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    ultima_ejecucion TIMESTAMP WITH TIME ZONE,
    proxima_ejecucion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comparativas_plataformas (
    id SERIAL PRIMARY KEY,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    data_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mejores_horarios (
    id SERIAL PRIMARY KEY,
    plataforma VARCHAR(50) NOT NULL,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 0 AND 6),
    hora INTEGER NOT NULL CHECK (hora BETWEEN 0 AND 23),
    promedio_engagement DECIMAL(10,2) DEFAULT 0.00,
    total_posts INTEGER DEFAULT 0,
    total_vistas INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    calculado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plataforma, dia_semana, hora)
);

CREATE TABLE IF NOT EXISTS alertas_metricas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    tipo_alerta VARCHAR(50) NOT NULL CHECK (tipo_alerta IN ('threshold', 'trending', 'anomaly')),
    condicion JSONB NOT NULL,
    plataformas TEXT[] DEFAULT ARRAY['instagram', 'twitter', 'linkedin', 'tiktok', 'youtube'],
    accion VARCHAR(50) NOT NULL CHECK (accion IN ('email', 'webhook', 'log')),
    destino VARCHAR(255),
    activa BOOLEAN DEFAULT TRUE,
    ultima_vez_disparada TIMESTAMP WITH TIME ZONE,
    veces_disparada INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_metricas_posts_updated_at BEFORE UPDATE ON metricas_posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();