from flask import Blueprint, request, jsonify
from modules.voice_agents.handlers.webhook_handler import WebhookHandler
from modules.voice_agents.services.voice_service import VoiceAgentService

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')
webhook_handler = WebhookHandler()
voice_service = VoiceAgentService()

@voice_bp.route('/webhook', methods=['POST'])
def retell_webhook():
    """Recibe webhooks de Retell AI"""
    try:
        data = request.json
        event = data.get('event')
        call = data.get('call', {})
        
        if event == 'call_started':
            webhook_handler.handle_call_started(call)
        elif event == 'call_ended':
            webhook_handler.handle_call_ended(call)
        elif event == 'call_analyzed':
            webhook_handler.handle_call_analyzed(call)
        
        return '', 204
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/get-customer-data', methods=['POST'])
def get_customer_data():
    """Custom function para el agente"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        
        customer_data = {
            'name': 'Juan Pérez',
            'plan': 'Premium',
            'status': 'active'
        }
        
        return jsonify(customer_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@voice_bp.route('/make-call', methods=['POST'])
def make_call():
    """Crear llamada saliente desde tu app"""
    try:
        data = request.json
        phone_number = data.get('phone_number')
        metadata = data.get('metadata', {})
        
        call = voice_service.make_outbound_call(phone_number, metadata)
        
        return jsonify({
            'success': True,
            'call_id': call.call_id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500