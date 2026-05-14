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
from auth import require_module
from social_publisher import social_bp
from analytics import analytics_bp
from stripe_webhooks import stripe_bp
app.register_blueprint(stripe_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(social_bp)
app.register_blueprint(admin_bp)

# Voice Agents Module
from api.voice.routes import voice_bp
app.register_blueprint(voice_bp)

CORS(app, resources={r"/api/*": {"origins": "*"}})

# Inicializar tablas al startup — envuelto en try/except para no crashear si DB no responde
try:
    init_leads_table()
    print("DB initialized successfully")
except Exception as e:
    print(f"Warning: Could not init leads table: {e}")


@app.route('/api/lead', methods=['POST'])
def capture_lead():
    """
    Endpoint para capturar leads desde formularios web
    """
    try:
        data = request.get_json()

        if not data.get('nombre') or not data.get('email') or not data.get('mensaje'):
            return jsonify({
                'success': False,
                'error': 'Campos requeridos: nombre, email, mensaje'
            }), 400

        lead_id = add_lead(
            nombre=data['nombre'],
            email=data['email'],
            telefono=data.get('telefono'),
            empresa=data.get('empresa'),
            mensaje=data['mensaje'],
            fuente=data.get('fuente', 'web')
        )

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
@require_module('leads')
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
@require_module('leads')
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
@require_module('leads')
def get_stats():
    """Estadisticas del pipeline"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT estado, COUNT(*) as cantidad, AVG(score) as score_promedio
            FROM leads
            GROUP BY estado
        """)

        stats_por_estado = {}
        for row in cursor.fetchall():
            stats_por_estado[row[0]] = {
                'cantidad': row[1],
                'score_promedio': round(row[2], 1) if row[2] else 0
            }

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
    return jsonify({'status': 'ok', 'service': 'nowcustom-api'})


@app.route('/')
def index():
    return jsonify({'service': 'NowCustom API', 'status': 'running'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)