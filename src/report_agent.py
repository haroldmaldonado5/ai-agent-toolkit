import sqlite3
from datetime import datetime, timedelta

def generar_reporte_semanal():
    # Conectar a la base de datos
    conn = sqlite3.connect('C:/Users/cu5to/databases/consultora.db')
    cursor = conn.cursor()
    
    # Fecha de hoy y hace 7 días
    hoy = datetime.now()
    hace_7_dias = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print("=" * 60)
    print("📊 REPORTE SEMANAL - CONSULTORA")
    print(f"Período: {hace_7_dias} a {hoy.strftime('%Y-%m-%d')}")
    print("=" * 60)
    print()
    
    # 1. HORAS FACTURABLES POR PROYECTO
    print("🕐 HORAS FACTURABLES POR PROYECTO (últimos 7 días)")
    print("-" * 60)
    cursor.execute('''
        SELECT p.nombre, SUM(h.horas) as total_horas, p.tarifa_por_hora,
               SUM(h.horas * p.tarifa_por_hora) as monto_facturado
        FROM horas_trabajadas h
        JOIN proyectos p ON h.proyecto_id = p.id
        WHERE h.fecha >= ?
        GROUP BY p.id
        ORDER BY total_horas DESC
    ''', (hace_7_dias,))
    
    total_horas = 0
    total_facturado = 0
    
    for proyecto, horas, tarifa, monto in cursor.fetchall():
        print(f"  • {proyecto}")
        print(f"    Horas: {horas:.1f}h | Tarifa: ${tarifa}/h | Total: ${monto:,.2f}")
        total_horas += horas
        total_facturado += monto
    
    print(f"\n  TOTAL SEMANAL: {total_horas:.1f} horas | ${total_facturado:,.2f}")
    print()
    
    # 2. CLIENTES ACTIVOS VS INACTIVOS
    print("👥 ESTADO DE CLIENTES")
    print("-" * 60)
    cursor.execute("SELECT estado, COUNT(*) FROM clientes GROUP BY estado")
    for estado, cantidad in cursor.fetchall():
        emoji = "✅" if estado == "activo" else "⏸️"
        print(f"  {emoji} {estado.capitalize()}: {cantidad}")
    print()
    
    # 3. INGRESOS SEMANALES
    print("💰 INGRESOS SEMANALES")
    print("-" * 60)
    cursor.execute('''
        SELECT SUM(monto), COUNT(*)
        FROM ingresos
        WHERE fecha >= ?
    ''', (hace_7_dias,))
    
    ingresos_total, num_transacciones = cursor.fetchone()
    if ingresos_total:
        print(f"  Total ingresado: ${ingresos_total:,.2f}")
        print(f"  Transacciones: {num_transacciones}")
        
        # Detalle de ingresos
        cursor.execute('''
            SELECT i.fecha, p.nombre, i.monto, i.concepto
            FROM ingresos i
            JOIN proyectos p ON i.proyecto_id = p.id
            WHERE i.fecha >= ?
            ORDER BY i.fecha DESC
        ''', (hace_7_dias,))
        
        print("\n  Detalle:")
        for fecha, proyecto, monto, concepto in cursor.fetchall():
            print(f"    • {fecha} | {proyecto} | ${monto:,.2f} | {concepto}")
    else:
        print("  No hay ingresos registrados esta semana")
    print()
    
    # 4. TAREAS PENDIENTES POR CLIENTE
    print("📋 TAREAS PENDIENTES")
    print("-" * 60)
    cursor.execute('''
        SELECT c.nombre, t.descripcion, t.prioridad, t.fecha_vencimiento
        FROM tareas t
        JOIN clientes c ON t.cliente_id = c.id
        WHERE t.completada = 0
        ORDER BY 
            CASE t.prioridad 
                WHEN 'alta' THEN 1 
                WHEN 'media' THEN 2 
                WHEN 'baja' THEN 3 
            END,
            t.fecha_vencimiento
    ''')
    
    for cliente, descripcion, prioridad, vencimiento in cursor.fetchall():
        emoji_prioridad = "🔴" if prioridad == "alta" else "🟡" if prioridad == "media" else "🟢"
        print(f"  {emoji_prioridad} [{prioridad.upper()}] {cliente}")
        print(f"    {descripcion}")
        print(f"    Vencimiento: {vencimiento}")
        print()
    
    print("=" * 60)
    print("✅ Reporte generado exitosamente")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    generar_reporte_semanal()