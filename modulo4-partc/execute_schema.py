import psycopg2

DATABASE_URL = "postgresql://postgres:mMHncOWfGTQCkJmcPXPdXfGipBKUHeQt@maglev.proxy.rlwy.net:12464/railway"

print("\n🔄 Conectando a Railway PostgreSQL...")

statements = [
    # Tabla 1: metricas_posts
    """CREATE TABLE IF NOT EXISTS metricas_posts (
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
    )""",
    
    # Indices tabla 1
    "CREATE INDEX IF NOT EXISTS idx_metricas_plataforma ON metricas_posts(plataforma)",
    "CREATE INDEX IF NOT EXISTS idx_metricas_timestamp ON metricas_posts(timestamp DESC)",
    
    # Tabla 2: reportes_programados
    """CREATE TABLE IF NOT EXISTS reportes_programados (
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
    )""",
    
    # Tabla 3: comparativas_plataformas
    """CREATE TABLE IF NOT EXISTS comparativas_plataformas (
        id SERIAL PRIMARY KEY,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE NOT NULL,
        data_json JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )""",
    
    # Tabla 4: mejores_horarios
    """CREATE TABLE IF NOT EXISTS mejores_horarios (
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
    )""",
    
    # Tabla 5: alertas_metricas
    """CREATE TABLE IF NOT EXISTS alertas_metricas (
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
    )""",
    
    # Funcion update_updated_at
    """CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql'""",
    
    # Trigger
    """CREATE TRIGGER update_metricas_posts_updated_at 
    BEFORE UPDATE ON metricas_posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"""
]

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("✅ Conexión exitosa\n")
    
    for i, stmt in enumerate(statements, 1):
        try:
            cursor.execute(stmt)
            conn.commit()
            print(f"  ✅ Statement {i}/{len(statements)} ejecutado")
        except Exception as e:
            print(f"  ⚠️ Statement {i}: {str(e)[:80]}")
            conn.rollback()
    
    # Verificar tablas
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    print(f"\n📊 TABLAS CREADAS ({len(tables)}):")
    for t in tables:
        print(f"  ✅ {t[0]}")
    
    print("\n✅ SCHEMA INSTALADO EXITOSAMENTE\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()