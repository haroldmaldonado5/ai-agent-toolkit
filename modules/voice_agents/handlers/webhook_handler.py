from modules.voice_agents.services.voice_service import VoiceAgentService

class WebhookHandler:
    def __init__(self):
        self.voice_service = VoiceAgentService()
    
    def handle_call_started(self, data):
        """Cuando inicia una llamada"""
        print(f"Llamada iniciada: {data.get('call_id')}")
    
    def handle_call_ended(self, data):
        """Cuando termina una llamada"""
        print(f"Llamada finalizada: {data.get('call_id')}")
        print(f"Duración: {data.get('call_length')} segundos")
        
        self.voice_service.save_conversation(data)
    
    def handle_call_analyzed(self, data):
        """Cuando se completa el análisis"""
        print(f"Análisis completado: {data.get('call_id')}")
        analysis = data.get('call_analysis', {})
        print(f"Sentimiento: {analysis.get('sentiment')}")