"""
Módulo 4C - Analytics Dashboard
Abstracción de base de datos: SQLite (local) / PostgreSQL (Railway)
"""

import os
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
USE_POSTGRESQL = DATABASE_URL is not None and DATABASE_URL.startswith('postgresql')

if USE_POSTGRESQL:
    print("🔵 Usando Railway PostgreSQL")
    import psycopg2
else:
    print("🟢 Usando SQLite local")
    import sqlite3


class Database:
    def __init__(self):
        self.use_postgresql = USE_POSTGRESQL
        self.database_url = DATABASE_URL
        
    def get_connection(self):
        if self.use_postgresql:
            return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        else:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'databases', 'analytics.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if self.use_postgresql:
                results = cursor.fetchall()
            else:
                results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            
            if self.use_postgresql:
                cursor.execute("SELECT LASTVAL()")
                last_id = cursor.fetchone()[0]
            else:
                last_id = cursor.lastrowid
            return last_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error en INSERT: {e}")
            raise
        finally:
            cursor.close()
            conn.close()


db = Database()


def get_metrics_by_platform(platform: str, limit: int = 100) -> List[Dict[str, Any]]:
    query = """
        SELECT * FROM metricas_posts
        WHERE plataforma = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """ if db.use_postgresql else """
        SELECT * FROM metricas_posts
        WHERE plataforma = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    return db.execute_query(query, (platform, limit))


def insert_metrics(post_id: str, platform: str, metrics: Dict[str, int]) -> Optional[int]:
    query = """
        INSERT INTO metricas_posts (
            post_id, plataforma, vistas, likes, comentarios, 
            shares, reach, impressions, engagement_rate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """ if db.use_postgresql else """
        INSERT INTO metricas_posts (
            post_id, plataforma, vistas, likes, comentarios, 
            shares, reach, impressions, engagement_rate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        post_id, platform,
        metrics.get('vistas', 0),
        metrics.get('likes', 0),
        metrics.get('comentarios', 0),
        metrics.get('shares', 0),
        metrics.get('reach', 0),
        metrics.get('impressions', 0),
        metrics.get('engagement_rate', 0.0)
    )
    return db.execute_insert(query, params)


def get_platform_comparison(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    query = """
        SELECT 
            plataforma,
            COUNT(*) as total_posts,
            SUM(vistas) as total_vistas,
            SUM(likes) as total_likes,
            SUM(comentarios) as total_comentarios,
            SUM(shares) as total_shares,
            AVG(engagement_rate) as promedio_engagement
        FROM metricas_posts
        WHERE timestamp BETWEEN %s AND %s
        GROUP BY plataforma
        ORDER BY total_vistas DESC
    """ if db.use_postgresql else """
        SELECT 
            plataforma,
            COUNT(*) as total_posts,
            SUM(vistas) as total_vistas,
            SUM(likes) as total_likes,
            SUM(comentarios) as total_comentarios,
            SUM(shares) as total_shares,
            AVG(engagement_rate) as promedio_engagement
        FROM metricas_posts
        WHERE timestamp BETWEEN ? AND ?
        GROUP BY plataforma
        ORDER BY total_vistas DESC
    """
    return db.execute_query(query, (start_date, end_date))