"""
Database abstraction layer
- Railway/producción: PostgreSQL vía DATABASE_URL
- Local: SQLite fallback
"""

import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL')

# Railway a veces devuelve 'postgres://', psycopg necesita 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USING_POSTGRES = bool(DATABASE_URL)

# Ruta SQLite para desarrollo local
SQLITE_PATH = os.environ.get(
    'DB_PATH',
    os.path.join(os.path.dirname(__file__), 'data', 'leads.db')
)
if not USING_POSTGRES:
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)


def get_connection():
    """Devuelve una conexión a la base de datos activa."""
    if USING_POSTGRES:
        import psycopg
        return psycopg.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row  # acceso por nombre de columna
        return conn


def adapt_query(query):
    """
    Convierte placeholders ? (SQLite) a %s (PostgreSQL) si está en producción.
    Permite escribir siempre con ? en el código fuente.
    """
    if USING_POSTGRES:
        return query.replace('?', '%s')
    return query


def last_insert_id(cursor):
    """Devuelve el ID del último INSERT de forma compatible."""
    if USING_POSTGRES:
        return cursor.fetchone()[0]
    return cursor.lastrowid
