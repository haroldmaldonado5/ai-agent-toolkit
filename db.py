"""
Database abstraction layer
- Render/produccion: PostgreSQL via DATABASE_URL (Supabase pooler IPv4)
- Local: SQLite fallback
"""
import os
import sqlite3
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USING_POSTGRES = bool(DATABASE_URL)

SQLITE_PATH = os.environ.get(
    'DB_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'leads.db')
)

if not USING_POSTGRES:
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

def _parse_db_url(url):
    """Parsea DATABASE_URL en parametros individuales para psycopg."""
    parsed = urlparse(url.split('?')[0])
    params = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'dbname': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'sslmode': 'require',
        'connect_timeout': 10,
    }
    return params

def get_connection():
    """Devuelve una conexion a la base de datos activa."""
    if USING_POSTGRES:
        import psycopg
        params = _parse_db_url(DATABASE_URL)
        return psycopg.connect(**params)
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