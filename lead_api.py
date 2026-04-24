"""
Lead Capture API - Servidor Flask para recibir formularios
Recibe leads del formulario web y los guarda en la base de datos
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# Importar funciones del lead_manager y capa de base de datos
import sys
sys.path.append(os.path.dirname(__file__))
from db import get_connection, adapt_query
from lead_manager import add_lead, calculate_lead_score, init_leads_table

app = Flask(__name__)
from tenant_admin import admin_bp
app.register_blueprint(admin_bp)

CORS(app, resources={r"/api/*": {"origins": "*"}})  # Permitir peticiones desde Framer y otros orÃ­genes
# Inicializar tablas al startup (necesario para gunicorn/Railway)
init_leads_table()

@app.route('/api/lead', methods=['POST'])
def capture_lead():
    """
    Endpoint para capturar leads desde formularios web
    
    Recibe JSON:
    {
        "nombre": "Juan PÃƒÂ©rez",
        "email": "juan@empresa.com",
        "telefono": "555-1234",
        "empresa": "Empresa XYZ",
        "mensaje": "Me interesa...",
        "fuente": "web_form"
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('nombre') or not data.get('email') or not data.get('mensaje'):
            return jsonify({
                'success': False,
                'error': 'Campos requeridos: nombre, email, mensaje'
            }), 400
        
        # Agregar lead
        lead_id = add_lead(
            nombre=data['nombre'],
            email=data['email'],
            telefono=data.get('telefono'),
            empresa=data.get('empresa'),
            mensaje=data['mensaje'],
            fuente=data.get('fuente', 'web')
        )
        
        # TODO: AquÃƒÂ­ enviar email de notificaciÃƒÂ³n
        # TODO: AquÃƒÂ­ enviar email de bienvenida al lead
        
        return jsonify({
            'success': True,
            'lead_id': lead_id,
            'message': 'Lead capturado exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error capturando lead: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500


@app.route('/api/leads', methods=['GET'])
def get_leads_api():
    """Obtiene lista de leads"""
    try:
        estado = request.args.get('estado')
        min_score = int(request.args.get('min_score', 0))

        conn = get_connection()
        cursor = conn.cursor()

        query = adapt_query("SELECT * FROM leads WHERE score >= ?")
        params = [min_score]

        if estado:
            query += adapt_query(" AND estado = ?")
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
                'fecha_captura': str(row[9])
            })

        conn.close()

        return jsonify({
            'success': True,
            'leads': leads,
            'total': len(leads)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/lead/<int:lead_id>/estado', methods=['PUT'])
def update_lead_estado_api(lead_id):
    """Actualiza estado de un lead"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        notas = data.get('notas')

        if not nuevo_estado:
            return jsonify({
                'success': False,
                'error': 'Estado requerido'
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        update_q = adapt_query("""
            UPDATE leads
            SET estado = ?, notas = COALESCE(?, notas)
            WHERE id = ?
        """)
        cursor.execute(update_q, (nuevo_estado, notas, lead_id))

        insert_q = adapt_query("""
            INSERT INTO lead_actividad (lead_id, tipo, descripcion)
            VALUES (?, ?, ?)
        """)
        cursor.execute(insert_q, (lead_id, 'estado_cambio', f'Estado cambiado a: {nuevo_estado}'))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Lead {lead_id} actualizado'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """EstadÃ­sticas del pipeline"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Stats por estado
        cursor.execute("""
            SELECT
                estado,
                COUNT(*) as cantidad,
                AVG(score) as score_promedio
            FROM leads
            GROUP BY estado
        """)

        stats_por_estado = {}
        for row in cursor.fetchall():
            stats_por_estado[row[0]] = {
                'cantidad': row[1],
                'score_promedio': round(row[2], 1) if row[2] else 0
            }

        # Stats generales
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads WHERE estado = 'nuevo'")
        leads_nuevos = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(score) FROM leads")
        score_promedio = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_leads': total_leads,
                'leads_nuevos': leads_nuevos,
                'score_promedio': round(score_promedio, 1) if score_promedio else 0,
                'por_estado': stats_por_estado
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'lead-capture-api'})


@app.route('/')
def index():
    """Sirve el formulario HTML"""
    from flask import send_file
    return send_file('lead_capture_form.html')


if __name__ == '__main__':
    print("Ã°Å¸Å¡â‚¬ LEAD CAPTURE API")
    print("Ã°Å¸â€œÂ Inicializando base de datos...")
    init_leads_table()
    print("Ã¢Å“â€¦ Listo\n")
    print("Ã°Å¸â€œÂ¡ API corriendo en: http://localhost:5000")
    print("Ã°Å¸â€œÂ Endpoints:")
    print("   POST   /api/lead          - Capturar nuevo lead")
    print("   GET    /api/leads         - Listar leads")
    print("   PUT    /api/lead/:id/estado - Actualizar estado")
    print("   GET    /api/stats         - EstadÃƒÂ­sticas")
    print("   GET    /health            - Health check")
    print("\nÃ°Å¸â€Â¥ Presiona Ctrl+C para detener\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)