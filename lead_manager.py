"""
Lead Management System - Backend
Captura, almacena y gestiona leads automáticamente
"""

import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.expanduser("~/databases/consultora.db")


def init_leads_table():
    """Crea tabla de leads si no existe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT,
            empresa TEXT,
            mensaje TEXT,
            fuente TEXT,
            estado TEXT DEFAULT 'nuevo',
            score INTEGER DEFAULT 0,
            fecha_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_seguimiento TIMESTAMP,
            asignado_a TEXT,
            notas TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_actividad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            tipo TEXT,
            descripcion TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tablas de leads creadas")


def calculate_lead_score(lead_data):
    """
    Calcula score del lead (0-100)
    
    Criterios:
    - Tiene email: +20
    - Tiene teléfono: +15
    - Tiene empresa: +15
    - Mensaje largo (>50 chars): +20
    - Email corporativo (@empresa.com): +30
    """
    score = 0
    
    if lead_data.get('email'):
        score += 20
        if '@' in lead_data['email'] and not any(
            domain in lead_data['email'].lower() 
            for domain in ['gmail', 'yahoo', 'hotmail', 'outlook']
        ):
            score += 30  # Email corporativo
    
    if lead_data.get('telefono'):
        score += 15
    
    if lead_data.get('empresa'):
        score += 15
    
    if lead_data.get('mensaje') and len(lead_data['mensaje']) > 50:
        score += 20
    
    return min(score, 100)


def add_lead(nombre, email, telefono=None, empresa=None, mensaje=None, fuente='web'):
    """Agrega nuevo lead a la base de datos"""
    
    lead_data = {
        'nombre': nombre,
        'email': email,
        'telefono': telefono,
        'empresa': empresa,
        'mensaje': mensaje,
        'fuente': fuente
    }
    
    score = calculate_lead_score(lead_data)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO leads (nombre, email, telefono, empresa, mensaje, fuente, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, email, telefono, empresa, mensaje, fuente, score))
    
    lead_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO lead_actividad (lead_id, tipo, descripcion)
        VALUES (?, ?, ?)
    """, (lead_id, 'captura', f'Lead capturado desde {fuente}'))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Lead agregado: {nombre} (Score: {score})")
    return lead_id


def get_leads(estado=None, min_score=0):
    """Obtiene leads filtrados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE score >= ?"
    params = [min_score]
    
    if estado:
        query += " AND estado = ?"
        params.append(estado)
    
    query += " ORDER BY score DESC, fecha_captura DESC"
    
    cursor.execute(query, params)
    
    leads = []
    for row in cursor.fetchall():
        leads.append({
            'id': row[0],
            'nombre': row[1],
            'email': row[2],
            'telefono': row[3],
            'empresa': row[4],
            'mensaje': row[5],
            'fuente': row[6],
            'estado': row[7],
            'score': row[8],
            'fecha_captura': row[9]
        })
    
    conn.close()
    return leads


def update_lead_estado(lead_id, nuevo_estado, notas=None):
    """Actualiza estado de un lead"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE leads 
        SET estado = ?, notas = COALESCE(?, notas)
        WHERE id = ?
    """, (nuevo_estado, notas, lead_id))
    
    cursor.execute("""
        INSERT INTO lead_actividad (lead_id, tipo, descripcion)
        VALUES (?, ?, ?)
    """, (lead_id, 'estado_cambio', f'Estado cambiado a: {nuevo_estado}'))
    
    conn.commit()
    conn.close()
    print(f"✅ Lead {lead_id} actualizado a: {nuevo_estado}")


def get_pipeline_stats():
    """Estadísticas del pipeline de ventas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            estado,
            COUNT(*) as cantidad,
            AVG(score) as score_promedio
        FROM leads
        GROUP BY estado
    """)
    
    stats = {}
    for row in cursor.fetchall():
        stats[row[0]] = {
            'cantidad': row[1],
            'score_promedio': round(row[2], 1) if row[2] else 0
        }
    
    conn.close()
    return stats


if __name__ == '__main__':
    print("🎯 LEAD MANAGEMENT SYSTEM\n")
    
    # Inicializar tablas
    init_leads_table()
    
    # Ejemplo: Agregar lead de prueba
    print("\n📝 Agregando lead de prueba...")
    add_lead(
        nombre="Juan Pérez",
        email="juan@empresa.com",
        telefono="555-1234",
        empresa="Empresa XYZ",
        mensaje="Me interesa automatizar mi negocio. Tengo una consultora de salud.",
        fuente="landing_page"
    )
    
    # Ver leads
    print("\n📊 Leads capturados:")
    leads = get_leads()
    for lead in leads:
        print(f"  {lead['nombre']} - {lead['email']} (Score: {lead['score']})")
    
    # Pipeline stats
    print("\n📈 Pipeline Stats:")
    stats = get_pipeline_stats()
    for estado, data in stats.items():
        print(f"  {estado}: {data['cantidad']} leads (Score promedio: {data['score_promedio']})")