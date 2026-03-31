#!/usr/bin/env python3
"""
Generador de Reportes para Consultora
Extrae datos de SQLite y crea Google Docs con reportes formateados
"""

import sqlite3
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Scopes necesarios para Google Docs y Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

# Rutas de configuración
CREDENTIALS_PATH = os.path.expanduser('~/.config/google-drive-mcp/gcp-oauth.keys.json')
TOKEN_PATH = os.path.expanduser('~/.config/google-drive-mcp/tokens.pickle')
DB_PATH = os.path.expanduser('~/databases/consultora.db')


def get_google_credentials():
    """Obtiene o genera credenciales de Google OAuth"""
    creds = None
    
    # Intentar cargar tokens existentes
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, generar nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para próxima ejecución
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds


def get_db_data():
    """Extrae datos de la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    data = {}
    
    # Clientes activos
    cursor.execute("""
        SELECT nombre, contacto_email, fecha_inicio 
        FROM clientes 
        WHERE estado = 'activo'
        ORDER BY nombre
    """)
    data['clientes_activos'] = cursor.fetchall()
    
    # Proyectos activos con horas
    cursor.execute("""
        SELECT 
            c.nombre as cliente,
            p.nombre as proyecto,
            p.horas_estimadas,
            p.horas_facturadas,
            p.tarifa_por_hora,
            (p.horas_facturadas * p.tarifa_por_hora) as facturado,
            p.estado
        FROM proyectos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.estado IN ('activo', 'completado')
        ORDER BY p.estado, c.nombre
    """)
    data['proyectos'] = cursor.fetchall()
    
    # Total de ingresos por mes
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', fecha) as mes,
            SUM(monto) as total
        FROM ingresos
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 6
    """)
    data['ingresos_mensuales'] = cursor.fetchall()
    
    # Tareas pendientes de alta prioridad
    cursor.execute("""
        SELECT 
            c.nombre as cliente,
            t.descripcion,
            t.fecha_vencimiento
        FROM tareas t
        JOIN clientes c ON t.cliente_id = c.id
        WHERE t.completada = 0 AND t.prioridad = 'alta'
        ORDER BY t.fecha_vencimiento
    """)
    data['tareas_pendientes'] = cursor.fetchall()
    
    conn.close()
    return data


def create_google_doc(creds, data):
    """Crea un Google Doc con el reporte"""
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Crear documento
    title = f"Reporte Consultora - {datetime.now().strftime('%Y-%m-%d')}"
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc['documentId']
    
    # Construir contenido del documento
    requests = []
    
    # Título principal
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': f'{title}\n\n'
        }
    })
    
    # Sección: Clientes Activos
    text = '📊 CLIENTES ACTIVOS\n\n'
    for nombre, email, fecha_inicio in data['clientes_activos']:
        text += f'• {nombre}\n  Email: {email}\n  Desde: {fecha_inicio}\n\n'
    
    # Sección: Proyectos
    text += '\n💼 PROYECTOS\n\n'
    for cliente, proyecto, estimadas, facturadas, tarifa, total, estado in data['proyectos']:
        estado_emoji = '✅' if estado == 'completado' else '🔄'
        text += f'{estado_emoji} {cliente} - {proyecto}\n'
        text += f'  Horas: {facturadas}/{estimadas} | Tarifa: ${tarifa}/hr | Total: ${total:.2f}\n\n'
    
    # Sección: Ingresos
    text += '\n💰 INGRESOS MENSUALES (últimos 6 meses)\n\n'
    for mes, total in data['ingresos_mensuales']:
        text += f'{mes}: ${total:,.2f}\n'
    
    # Sección: Tareas Pendientes
    text += '\n\n⚠️ TAREAS PENDIENTES (ALTA PRIORIDAD)\n\n'
    if data['tareas_pendientes']:
        for cliente, descripcion, vencimiento in data['tareas_pendientes']:
            text += f'• {cliente}: {descripcion}\n  Vencimiento: {vencimiento}\n\n'
    else:
        text += 'No hay tareas de alta prioridad pendientes.\n'
    
    # Insertar todo el texto
    requests.append({
        'insertText': {
            'location': {'index': 1},
            'text': text
        }
    })
    
    # Aplicar formato
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={'requests': requests}
    ).execute()
    
    # Obtener URL del documento
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    
    print(f'\n✅ Reporte creado exitosamente!')
    print(f'📄 URL: {doc_url}')
    print(f'📋 ID del documento: {doc_id}')
    
    return doc_id, doc_url


def main():
    """Función principal"""
    print('🚀 Generando reporte de consultora...\n')
    
    # Verificar que exista la base de datos
    if not os.path.exists(DB_PATH):
        print(f'❌ Error: No se encontró la base de datos en {DB_PATH}')
        return
    
    # Verificar que existan las credenciales
    if not os.path.exists(CREDENTIALS_PATH):
        print(f'❌ Error: No se encontraron credenciales en {CREDENTIALS_PATH}')
        return
    
    try:
        # Autenticar con Google
        print('🔐 Autenticando con Google...')
        creds = get_google_credentials()
        
        # Extraer datos
        print('📊 Extrayendo datos de la base de datos...')
        data = get_db_data()
        
        # Crear documento
        print('📝 Creando Google Doc...')
        doc_id, doc_url = create_google_doc(creds, data)
        
        print('\n✨ ¡Proceso completado!')
        
    except Exception as e:
        print(f'\n❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()