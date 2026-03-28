import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('C:/Users/cu5to/databases/consultora.db')
cursor = conn.cursor()

# CLIENTES
clientes = [
    ('Tech Solutions SA', 'activo', '2025-01-15', 'contacto@techsolutions.com'),
    ('Marketing Pro', 'activo', '2025-02-01', 'info@marketingpro.com'),
    ('Legal Advisors', 'inactivo', '2024-11-10', 'legal@advisors.com'),
    ('Finance Corp', 'activo', '2025-03-01', 'admin@financecorp.com'),
]

cursor.executemany('INSERT INTO clientes (nombre, estado, fecha_inicio, contacto_email) VALUES (?, ?, ?, ?)', clientes)

# PROYECTOS
proyectos = [
    (1, 'Implementación ERP', 120, 85, 150, '2025-01-20', 'activo'),
    (2, 'Campaña Digital Q1', 60, 45, 120, '2025-02-05', 'activo'),
    (3, 'Auditoría Legal', 40, 40, 200, '2024-12-01', 'completado'),
    (4, 'Asesoría Fiscal Anual', 80, 20, 180, '2025-03-10', 'activo'),
]

cursor.executemany('INSERT INTO proyectos (cliente_id, nombre, horas_estimadas, horas_facturadas, tarifa_por_hora, fecha_inicio, estado) VALUES (?, ?, ?, ?, ?, ?, ?)', proyectos)

# HORAS TRABAJADAS (última semana)
hoy = datetime.now()
horas = []
for i in range(7):
    fecha = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
    horas.append((1, fecha, random.uniform(4, 8), 'Desarrollo módulo financiero'))
    horas.append((2, fecha, random.uniform(3, 6), 'Diseño de ads'))
    horas.append((4, fecha, random.uniform(2, 5), 'Revisión fiscal'))

cursor.executemany('INSERT INTO horas_trabajadas (proyecto_id, fecha, horas, descripcion) VALUES (?, ?, ?, ?)', horas)

# TAREAS PENDIENTES
tareas = [
    (1, 'Reunión de seguimiento ERP', 'alta', (hoy + timedelta(days=2)).strftime('%Y-%m-%d'), 0),
    (2, 'Entregar reporte de métricas', 'media', (hoy + timedelta(days=5)).strftime('%Y-%m-%d'), 0),
    (4, 'Revisar documentos fiscales', 'alta', (hoy + timedelta(days=1)).strftime('%Y-%m-%d'), 0),
    (1, 'Capacitación usuarios', 'baja', (hoy + timedelta(days=10)).strftime('%Y-%m-%d'), 0),
]

cursor.executemany('INSERT INTO tareas (cliente_id, descripcion, prioridad, fecha_vencimiento, completada) VALUES (?, ?, ?, ?, ?)', tareas)

# INGRESOS (últimas 2 semanas)
ingresos = [
    (1, 12750, (hoy - timedelta(days=7)).strftime('%Y-%m-%d'), 'Pago parcial ERP'),
    (2, 5400, (hoy - timedelta(days=3)).strftime('%Y-%m-%d'), 'Factura campaña digital'),
    (4, 3600, (hoy - timedelta(days=1)).strftime('%Y-%m-%d'), 'Adelanto asesoría'),
]

cursor.executemany('INSERT INTO ingresos (proyecto_id, monto, fecha, concepto) VALUES (?, ?, ?, ?)', ingresos)

conn.commit()
print("✅ Datos de prueba insertados exitosamente")
print(f"   - {len(clientes)} clientes")
print(f"   - {len(proyectos)} proyectos")
print(f"   - {len(horas)} registros de horas")
print(f"   - {len(tareas)} tareas")
print(f"   - {len(ingresos)} ingresos")
conn.close()