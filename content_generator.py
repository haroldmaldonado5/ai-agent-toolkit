"""
Content Generator - Motor de contenido para marketing
Genera posts automáticos para redes sociales
NOTA: Se actualizará con Marketing Agency Skill Pack después de instalarlo
"""

import os
import json
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates', 'social_media_templates')


def load_template(template_name):
    """Carga una plantilla desde templates/social_media_templates"""
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def generate_instagram_post(business_type, topic, tone="profesional"):
    """Genera un post de Instagram"""
    content = {
        'hook': f'¿Sabías que...? 💡',
        'main_message': f'Como {business_type}, compartimos este tip sobre {topic}.',
        'call_to_action': '👉 Guarda este post\n💬 Déjanos un comentario',
        'hashtags': '#salud #bienestar #tips',
        'image_description': f'Imagen profesional sobre {topic}',
        'suggested_time': '10am-12pm o 7pm-9pm'
    }
    return content


def generate_linkedin_post(business_type, topic):
    """Genera un post de LinkedIn"""
    content = {
        'opening': f'En {business_type}, nos enfocamos en...',
        'body': f'Insights sobre {topic}.',
        'bullets': ['Mejora productividad', 'Reducción costos', 'Mayor satisfacción'],
        'closing': '¿Qué opinas?',
        'hashtags': '#negocios #emprendimiento'
    }
    return content


def generate_content_calendar(business_type, num_days=7):
    """Genera calendario de contenido"""
    topics = ['Tip del día', 'Mito vs Realidad', 'Caso éxito', 'Tutorial', 'Motivación']
    calendar = []
    for day in range(num_days):
        day_plan = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'posts': [
                {'platform': 'Instagram', 'time': '10:00 AM', 'topic': topics[day % len(topics)]},
                {'platform': 'LinkedIn', 'time': '12:00 PM', 'topic': topics[day % len(topics)]}
            ]
        }
        calendar.append(day_plan)
    return calendar


def main():
    """Demo del generador"""
    print('🎨 CONTENT GENERATOR\n')
    
    instagram = generate_instagram_post('consultora', 'hidratación')
    print(f"Instagram: {instagram['hook']}\n")
    
    linkedin = generate_linkedin_post('consultora', 'wellness')
    print(f"LinkedIn: {linkedin['opening']}\n")
    
    calendar = generate_content_calendar('consultora', 7)
    print(f"✅ Calendario: {len(calendar)} días\n")


if __name__ == '__main__':
    main()