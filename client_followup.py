"""
Client Follow-up Agent - Envía emails automáticos de seguimiento
Identifica clientes que necesitan atención y envía emails personalizados
"""

import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json

# Configuración
DB_PATH = os.path.expanduser('~/databases/consultora.db')
CONFIG_PATH = 'config/email_config.json'


def load_email_config():
    """Carga configuración de email desde archivo JSON"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    else:
        print(f'⚠️  Archivo de configuración no encontrado: {CONFIG_PATH}')
        print('💡 Creando plantilla de configuración...')
        
        os.makedirs('config', exist_ok=True)
        
        template = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "your-email@gmail.com",
            "password": "your-app-password",
            "from_name": "Your Name"
        }
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(template, f, indent=2)
        
        print(f'✅ Plantilla creada en: {CONFIG_PATH}')
        print('📝 Edita el archivo con tus credenciales antes de continuar')
        return None


def get_clients_needing_followup(days_since_last_contact=30):
    """Identifica clientes que necesitan seguimiento"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days_since_last_contact)).strftime('%Y-%m-%d')
    
    cursor.execute("""
        SELECT DISTINCT
            c.id,
            c.nombre,
            c.contacto_email,
            MAX(p.fecha_inicio) as ultimo_proyecto,
            c.telefono
        FROM clientes c
        LEFT JOIN proyectos p ON c.id = p.cliente_id
        WHERE c.estado = 'activo'
        GROUP BY c.id
        HAVING ultimo_proyecto < ? OR ultimo_proyecto IS NULL
        ORDER BY ultimo_proyecto ASC
    """, (cutoff_date,))
    
    clients = []
    for row in cursor.fetchall():
        clients.append({
            'id': row[0],
            'nombre': row[1],
            'email': row[2],
            'ultimo_proyecto': row[3],
            'telefono': row[4]
        })
    
    conn.close()
    return clients


def generate_followup_email(client, template='general'):
    """Genera contenido de email de seguimiento personalizado"""
    
    templates = {
        'general': {
            'subject': f"¿Cómo va todo, {client['nombre']}?",
            'body': f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h2 style="color: #4A90E2;">Hola {client['nombre']},</h2>
                    
                    <p>Espero que todo esté marchando bien.</p>
                    
                    <p>Ha pasado un tiempo desde nuestro último contacto y quería saber:</p>
                    
                    <ul>
                        <li>¿Cómo han estado las cosas?</li>
                        <li>¿Hay algo en lo que pueda ayudarte?</li>
                        <li>¿Tienes algún proyecto nuevo en mente?</li>
                    </ul>
                    
                    <p>Me encantaría ponerme al día. ¿Tienes 15 minutos para una llamada esta semana?</p>
                    
                    <p>Simplemente responde a este email.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos,<br>
                        <strong>{{{{from_name}}}}</strong><br>
                        <span style="color: #666;">{{{{email}}}}</span>
                    </p>
                </body>
                </html>
            """
        }
    }
    
    selected = templates.get(template, templates['general'])
    return (selected['subject'], selected['body'])


def send_email(to_email, to_name, subject, body_html, config):
    """Envía email via SMTP"""
    try:
        body_html = body_html.replace('{{{{from_name}}}}', config['from_name'])
        body_html = body_html.replace('{{{{email}}}}', config['email'])
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config['from_name']} <{config['email']}>"
        msg['To'] = f"{to_name} <{to_email}>"
        msg['Subject'] = subject
        
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email'], config['password'])
        server.send_message(msg)
        server.quit()
        
        print(f'✅ Email enviado a {to_name} ({to_email})')
        return True
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        return False


def log_interaction(client_id, interaction_type, notes):
    """Registra interacción en la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT,
            notas TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)
    
    cursor.execute("""
        INSERT INTO interacciones (cliente_id, tipo, notas)
        VALUES (?, ?, ?)
    """, (client_id, interaction_type, notes))
    
    conn.commit()
    conn.close()


def main():
    """Función principal"""
    print('📧 CLIENT FOLLOW-UP AGENT (SMTP)\n')
    
    config = load_email_config()
    
    if not config or config['email'] == 'your-email@gmail.com':
        print('\n⚠️  Configura config/email_config.json primero')
        return
    
    if not os.path.exists(DB_PATH):
        print(f'❌ Base de datos no encontrada: {DB_PATH}')
        return
    
    print('🔍 Buscando clientes...')
    clients = get_clients_needing_followup(days_since_last_contact=30)
    
    if not clients:
        print('✅ No hay clientes que necesiten seguimiento')
        return
    
    print(f'\n📋 {len(clients)} clientes encontrados:\n')
    for i, client in enumerate(clients, 1):
        print(f"{i}. {client['nombre']} ({client['email']})")
    
    response = input(f'\n📧 ¿Enviar emails? (SI/no): ')
    
    if response.upper() != 'SI':
        print('❌ Cancelado')
        return
    
    print('\n📤 Enviando...\n')
    sent = 0
    
    for client in clients:
        subject, body = generate_followup_email(client)
        
        if send_email(client['email'], client['nombre'], subject, body, config):
            log_interaction(client['id'], 'email_followup', f'Follow-up: {subject}')
            sent += 1
    
    print(f'\n✨ Completado: {sent}/{len(clients)} emails enviados')


if __name__ == '__main__':
    main()