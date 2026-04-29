from retell import Retell
from modules.voice_agents.config import RETELL_API_KEY, RETELL_AGENT_ID, RETELL_PHONE_NUMBER

class VoiceAgentService:
    def __init__(self):
        self.client = Retell(api_key=RETELL_API_KEY)
    
    def make_outbound_call(self, to_number, metadata=None):
        """Crear llamada saliente"""
        try:
            call = self.client.call.create_phone_call(
                from_number=RETELL_PHONE_NUMBER,
                to_number=to_number,
                override_agent_id=RETELL_AGENT_ID,
                metadata=metadata or {}
            )
            print(f"Llamada creada: {call.call_id}")
            return call
        except Exception as e:
            print(f"Error creando llamada: {e}")
            raise e
    
    def get_call_info(self, call_id):
        """Obtener información de una llamada"""
        try:
            call = self.client.call.retrieve(call_id)
            return call
        except Exception as e:
            print(f"Error obteniendo llamada: {e}")
            raise e
    
    def save_conversation(self, call_data):
        """Guardar conversación en DB"""
        print(f"Guardando conversación: {call_data.get('call_id')}")
        print(f"Transcripción: {call_data.get('transcript')}")
        
        # TODO: Implementar guardado en PostgreSQL
        
        return call_data