import sqlite3
from datetime import datetime, timedelta
import subprocess
import json

def generar_reporte_semanal():
    # Conectar a la base de datos
    conn = sqlite3.connect('C:/Users/cu5to/databases/consultora.db')
    cursor = conn.cursor()
    
    # Fecha de hoy y hace 7 días
    hoy = datetime.now()
    hace_7_dias = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Construir el contenido del reporte
    contenido = []
    contenido.append("=" * 60)
    contenido.append("📊 REPORTE SEMANAL - CONSULTORA")
    contenido.append(f"Período: {hace_7_dias} a {hoy.strftime('%Y-%m-%d')}")
    contenido.append("=" * 60)
    contenido.append("")
    
    # 1. HORAS FACTURABLES
    contenido.append("🕐 HORAS FACTURABLES POR PROYECTO (últimos 7 días)")
    contenido.append("-" * 60)
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
        contenido.append(f"  • {proyecto}")
        contenido.append(f"    Horas: {horas:.1f}h | Tarifa: ${tarifa}/h | Total: ${monto:,.2f}")
        total_horas += horas
        total_facturado += monto
    
    contenido.append(f"\n  TOTAL SEMANAL: {total_horas:.1f} horas | ${total_facturado:,.2f}")
    contenido.append("")
    
    # 2. CLIENTES
    contenido.append("👥 ESTADO DE CLIENTES")
    contenido.append("-" * 60)
    cursor.execute("SELECT estado, COUNT(*) FROM clientes GROUP BY estado")
    for estado, cantidad in cursor.fetchall():
        emoji = "✅" if estado == "activo" else "⏸️"
        contenido.append(f"  {emoji} {estado.capitalize()}: {cantidad}")
    contenido.append("")
    
    # 3. INGRESOS
    contenido.append("💰 INGRESOS SEMANALES")
    contenido.append("-" * 60)
    cursor.execute('''
        SELECT SUM(monto), COUNT(*)
        FROM ingresos
        WHERE fecha >= ?
    ''', (hace_7_dias,))
    
    ingresos_total, num_transacciones = cursor.fetchone()
    if ingresos_total:
        contenido.append(f"  Total ingresado: ${ingresos_total:,.2f}")
        contenido.append(f"  Transacciones: {num_transacciones}")
        contenido.append("")
        contenido.append("  Detalle:")
        
        cursor.execute('''
            SELECT i.fecha, p.nombre, i.monto, i.concepto
            FROM ingresos i
            JOIN proyectos p ON i.proyecto_id = p.id
            WHERE i.fecha >= ?
            ORDER BY i.fecha DESC
        ''', (hace_7_dias,))
        
        for fecha, proyecto, monto, concepto in cursor.fetchall():
            contenido.append(f"    • {fecha} | {proyecto} | ${monto:,.2f} | {concepto}")
    else:
        contenido.append("  No hay ingresos registrados esta semana")
    contenido.append("")
    
    # 4. TAREAS
    contenido.append("📋 TAREAS PENDIENTES")
    contenido.append("-" * 60)
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
        contenido.append(f"  {emoji_prioridad} [{prioridad.upper()}] {cliente}")
        contenido.append(f"    {descripcion}")
        contenido.append(f"    Vencimiento: {vencimiento}")
        contenido.append("")
    
    contenido.append("=" * 60)
    
    conn.close()
    
    # Unir todo el contenido
    reporte_completo = "\n".join(contenido)
    
    # Guardar en archivo temporal
    archivo_temp = f"C:/Users/cu5to/agent-toolkit/src/reporte_{hoy.strftime('%Y%m%d')}.txt"
    with open(archivo_temp, 'w', encoding='utf-8') as f:
        f.write(reporte_completo)
    
    print("✅ Reporte generado")
    print(f"📄 Archivo: {archivo_temp}")
    print(f"📊 Total: {total_horas:.1f}h | ${total_facturado:,.2f}")
    
    # Aquí integraremos Google Drive en el próximo paso
    print("\n🔄 Próximo: Subir a Google Docs automáticamente")
    
    return archivo_temp

if __name__ == "__main__":
    generar_reporte_semanal()


