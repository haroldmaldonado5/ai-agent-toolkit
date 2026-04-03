"""
Social Media Scheduler - Planifica y publica contenido automáticamente
Gestiona calendario de publicaciones para múltiples plataformas
"""

import sqlite3
import os
from datetime import datetime, timedelta
import json

DB_PATH = os.path.expanduser("~/databases/consultora.db")


def init_social_tables():
    """Crea tablas para social media management"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de publicaciones programadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publicaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plataforma TEXT NOT NULL,
            tipo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            imagen_url TEXT,
            hashtags TEXT,
            fecha_programada TIMESTAMP NOT NULL,
            fecha_publicada TIMESTAMP,
            estado TEXT DEFAULT 'draft',
            engagement JSON,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    # Tabla de métricas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metricas_sociales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publicacion_id INTEGER,
            plataforma TEXT,
            likes INTEGER DEFAULT 0,
            comentarios INTEGER DEFAULT 0,
            compartidos INTEGER DEFAULT 0,
            alcance INTEGER DEFAULT 0,
            fecha_metrica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (publicacion_id) REFERENCES publicaciones(id)
        )
    """)
    
    # Tabla de calendario editorial
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendario_editorial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            semana INTEGER,
            año INTEGER,
            lunes TEXT,
            martes TEXT,
            miercoles TEXT,
            jueves TEXT,
            viernes TEXT,
            sabado TEXT,
            domingo TEXT,
            cliente_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tablas de social media creadas")


def create_post(plataforma, contenido, fecha_programada, tipo='post', hashtags=None, cliente_id=None):
    """Crea una publicación programada"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hashtags_str = ' '.join(hashtags) if hashtags else ''
    
    cursor.execute("""
        INSERT INTO publicaciones 
        (plataforma, tipo, contenido, hashtags, fecha_programada, cliente_id, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'scheduled')
    """, (plataforma, tipo, contenido, hashtags_str, fecha_programada, cliente_id))
    
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"✅ Post programado para {plataforma} - ID: {post_id}")
    return post_id


def get_scheduled_posts(fecha_inicio=None, fecha_fin=None, plataforma=None):
    """Obtiene posts programados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM publicaciones WHERE estado = 'scheduled'"
    params = []
    
    if fecha_inicio:
        query += " AND fecha_programada >= ?"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND fecha_programada <= ?"
        params.append(fecha_fin)
    
    if plataforma:
        query += " AND plataforma = ?"
        params.append(plataforma)
    
    query += " ORDER BY fecha_programada ASC"
    
    cursor.execute(query, params)
    
    posts = []
    for row in cursor.fetchall():
        posts.append({
            'id': row[0],
            'plataforma': row[1],
            'tipo': row[2],
            'contenido': row[3],
            'imagen_url': row[4],
            'hashtags': row[5],
            'fecha_programada': row[6],
            'estado': row[8]
        })
    
    conn.close()
    return posts


def update_post_status(post_id, nuevo_estado, engagement_data=None):
    """Actualiza estado de una publicación"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if nuevo_estado == 'published':
        fecha_publicada = datetime.now().isoformat()
        cursor.execute("""
            UPDATE publicaciones 
            SET estado = ?, fecha_publicada = ?, engagement = ?
            WHERE id = ?
        """, (nuevo_estado, fecha_publicada, json.dumps(engagement_data) if engagement_data else None, post_id))
    else:
        cursor.execute("""
            UPDATE publicaciones 
            SET estado = ?
            WHERE id = ?
        """, (nuevo_estado, post_id))
    
    conn.commit()
    conn.close()
    print(f"✅ Post {post_id} actualizado a: {nuevo_estado}")


def generate_week_calendar(semana_numero=None, año=None):
    """Genera calendario editorial de la semana"""
    if not semana_numero:
        semana_numero = datetime.now().isocalendar()[1]
    if not año:
        año = datetime.now().year
    
    posts = get_scheduled_posts()
    
    calendario = {
        'lunes': [],
        'martes': [],
        'miercoles': [],
        'jueves': [],
        'viernes': [],
        'sabado': [],
        'domingo': []
    }
    
    dias_map = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    
    for post in posts:
        fecha = datetime.fromisoformat(post['fecha_programada'])
        if fecha.isocalendar()[1] == semana_numero and fecha.year == año:
            dia_nombre = dias_map[fecha.weekday()]
            calendario[dia_nombre].append({
                'hora': fecha.strftime('%H:%M'),
                'plataforma': post['plataforma'],
                'contenido': post['contenido'][:50] + '...'
            })
    
    return calendario


def bulk_schedule_from_calendar(contenido_calendario):
    """Programa posts en masa desde un calendario de contenido"""
    posts_creados = 0
    
    for fecha_str, posts in contenido_calendario.items():
        for post in posts:
            fecha_programada = f"{fecha_str} {post.get('hora', '10:00')}:00"
            create_post(
                plataforma=post['plataforma'],
                contenido=post['contenido'],
                fecha_programada=fecha_programada,
                hashtags=post.get('hashtags'),
                cliente_id=post.get('cliente_id')
            )
            posts_creados += 1
    
    print(f"✅ {posts_creados} posts programados en masa")
    return posts_creados


if __name__ == '__main__':
    print("📅 SOCIAL MEDIA SCHEDULER\n")
    
    init_social_tables()
    
    print("\n📝 Programando posts de ejemplo...")
    
    mañana_10am = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0)
    create_post(
        plataforma='instagram',
        contenido='¿Sabías que la automatización puede ahorrarte 10 horas semanales? 🚀',
        fecha_programada=mañana_10am.isoformat(),
        hashtags=['#automatizacion', '#productividad', '#negocio']
    )
    
    mañana_2pm = (datetime.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0)
    create_post(
        plataforma='linkedin',
        contenido='Descubre cómo las PYMEs están transformando sus operaciones con IA y automatización.',
        fecha_programada=mañana_2pm.isoformat(),
        hashtags=['#IA', '#Automatizacion', '#Negocios']
    )
    
    print("\n📋 Posts programados:")
    posts = get_scheduled_posts()
    for post in posts:
        print(f"  {post['plataforma']} - {post['fecha_programada']}")
        print(f"    {post['contenido'][:60]}...")
    
    print("\n📅 Calendario editorial:")
    cal = generate_week_calendar()
    for dia, posts in cal.items():
        if posts:
            print(f"\n  {dia.upper()}:")
            for p in posts:
                print(f"    {p['hora']} - {p['plataforma']}: {p['contenido']}")