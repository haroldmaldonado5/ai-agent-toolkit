"""
Database abstraction layer
- Render/produccion: PostgreSQL via DATABASE_URL (Supabase pooler IPv4)
- Local: SQLite fallback
"""
import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Normalizar postgres:// a postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Forzar sslmode=require para Supabase y evitar IPv6
if DATABASE_URL and '?' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + '?sslmode=require'
elif DATABASE_URL and 'sslmode' not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL + '&sslmode=require'

USING_POSTGRES = bool(DATABASE_URL)

# Ruta SQLite para desarrollo local
SQLITE_PATH = os.environ.get(
    'DB_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'leads.db')
)
if not USING_POSTGRES:
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)


def get_connection():
    """Devuelve una conexion a la base de datos activa."""
    if USING_POSTGRES:
        import psycopg
        return psycopg.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def adapt_query(query):
    """Convierte placeholders ? (SQLite) a %s (PostgreSQL)."""
    if USING_POSTGRES:
        return query.replace('?', '%s')
    return query


def last_insert_id(cursor):
    """Devuelve el ID del ultimo INSERT de forma compatible."""
    if USING_POSTGRES:
        return cursor.fetchone()[0]
    return cursor.lastrowid