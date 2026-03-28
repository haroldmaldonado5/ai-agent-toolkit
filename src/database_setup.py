import sqlite3
from datetime import datetime, timedelta
import random

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('C:/Users/cu5to/databases/consultora.db')
cursor = conn.cursor()

# TABLA 1: Clientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    estado TEXT NOT NULL CHECK(estado IN ('activo', 'inactivo')),
    fecha_inicio DATE,
    contacto_email TEXT
)
''')

# TABLA 2: Proyectos
cursor.execute('''
CREATE TABLE IF NOT EXISTS proyectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    nombre TEXT NOT NULL,
    horas_estimadas REAL,
    horas_facturadas REAL DEFAULT 0,
    tarifa_por_hora REAL,
    fecha_inicio DATE,
    estado TEXT CHECK(estado IN ('activo', 'completado', 'pausado')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
''')

# TABLA 3: Horas Trabajadas
cursor.execute('''
CREATE TABLE IF NOT EXISTS horas_trabajadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proyecto_id INTEGER,
    fecha DATE,
    horas REAL,
    descripcion TEXT,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
)
''')

# TABLA 4: Tareas Pendientes
cursor.execute('''
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    descripcion TEXT NOT NULL,
    prioridad TEXT CHECK(prioridad IN ('alta', 'media', 'baja')),
    fecha_vencimiento DATE,
    completada BOOLEAN DEFAULT 0,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)
''')

# TABLA 5: Ingresos
cursor.execute('''
CREATE TABLE IF NOT EXISTS ingresos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proyecto_id INTEGER,
    monto REAL,
    fecha DATE,
    concepto TEXT,
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
)
''')

conn.commit()
print("✅ Base de datos creada exitosamente en C:/Users/cu5to/databases/consultora.db")
conn.close()