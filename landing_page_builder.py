"""
Landing Page Builder - Genera landing pages completas para clientes
Usa Marketing Skills + Frontend-design + Templates
"""

import os
import json
from datetime import datetime


def generate_landing_page_content(business_info):
    """
    Genera contenido optimizado para landing page
    
    Args:
        business_info: {
            'name': 'Nombre del negocio',
            'industry': 'consultora/quiropractico/servicios',
            'value_prop': 'Propuesta de valor principal',
            'services': ['servicio1', 'servicio2'],
            'target_audience': 'descripción de audiencia',
            'contact': {...}
        }
    
    Returns:
        dict con todas las secciones de la landing page
    """
    
    content = {
        'meta': {
            'title': f"{business_info['name']} - {business_info.get('value_prop', 'Servicios Profesionales')}",
            'description': f"Expertos en {', '.join(business_info.get('services', [])[:3])}. {business_info.get('value_prop', '')}",
            'keywords': ', '.join(business_info.get('services', []))
        },
        
        'hero': {
            'headline': business_info.get('value_prop', f"{business_info['name']} - Servicios Profesionales"),
            'subheadline': f"Ayudamos a {business_info.get('target_audience', 'nuestros clientes')} a lograr sus objetivos",
            'cta_primary': 'Agendar Consulta Gratis',
            'cta_secondary': 'Conocer Más',
            'hero_image_alt': f"{business_info['name']} - Servicios profesionales"
        },
        
        'benefits': {
            'title': 'Por Qué Elegirnos',
            'items': [
                {
                    'icon': '✓',
                    'title': 'Experiencia Comprobada',
                    'description': 'Años de experiencia en la industria'
                },
                {
                    'icon': '⚡',
                    'title': 'Resultados Rápidos',
                    'description': 'Soluciones efectivas en tiempo récord'
                },
                {
                    'icon': '💯',
                    'title': 'Satisfacción Garantizada',
                    'description': 'Compromiso con la excelencia'
                }
            ]
        },
        
        'services': {
            'title': 'Nuestros Servicios',
            'items': []
        },
        
        'testimonials': {
            'title': 'Lo Que Dicen Nuestros Clientes',
            'items': [
                {
                    'text': 'Excelente servicio, resultados más allá de mis expectativas.',
                    'author': 'Cliente Satisfecho',
                    'role': 'Empresario',
                    'rating': 5
                },
                {
                    'text': 'Profesionales dedicados que realmente se preocupan por el éxito de sus clientes.',
                    'author': 'María González',
                    'role': 'Directora de Marketing',
                    'rating': 5
                }
            ]
        },
        
        'cta': {
            'title': '¿Listo para Comenzar?',
            'subtitle': 'Agenda tu consulta gratuita hoy mismo',
            'button_text': 'Agendar Ahora',
            'subtext': 'Sin compromiso. Cancelación gratuita.'
        },
        
        'contact': business_info.get('contact', {
            'email': 'contacto@empresa.com',
            'phone': '+1 (555) 123-4567',
            'address': 'Ciudad, País'
        })
    }
    
    # Generar descripción de servicios
    for service in business_info.get('services', []):
        content['services']['items'].append({
            'name': service,
            'description': f'Servicio profesional de {service} adaptado a tus necesidades',
            'icon': '🎯'
        })
    
    return content


def generate_landing_page_html(content, style='modern'):
    """
    Genera HTML completo de la landing page
    
    Args:
        content: dict con contenido (de generate_landing_page_content)
        style: 'modern', 'minimal', 'corporate'
    
    Returns:
        string con HTML completo
    """
    
    # Estilos según tema
    color_schemes = {
        'modern': {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'accent': '#f093fb'
        },
        'minimal': {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db'
        },
        'corporate': {
            'primary': '#1e3a8a',
            'secondary': '#1e40af',
            'accent': '#3b82f6'
        }
    }
    
    colors = color_schemes.get(style, color_schemes['modern'])
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content['meta']['description']}">
    <meta name="keywords" content="{content['meta']['keywords']}">
    <title>{content['meta']['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            padding: 100px 20px;
            text-align: center;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .hero h1 {{
            font-size: 3.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
        }}
        
        .hero p {{
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        .cta-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 1rem 2.5rem;
            font-size: 1.1rem;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: white;
            color: {colors['primary']};
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: white;
            border: 2px solid white;
        }}
        
        .btn-secondary:hover {{
            background: white;
            color: {colors['primary']};
        }}
        
        /* Benefits Section */
        .benefits {{
            padding: 80px 20px;
            background: #f8f9fa;
        }}
        
        .section-title {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: {colors['primary']};
        }}
        
        .benefits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}
        
        .benefit-card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .benefit-card:hover {{
            transform: translateY(-5px);
        }}
        
        .benefit-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .benefit-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: {colors['primary']};
        }}
        
        /* Services Section */
        .services {{
            padding: 80px 20px;
        }}
        
        .services-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
        }}
        
        .service-card {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            border-left: 4px solid {colors['primary']};
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        
        .service-card h3 {{
            color: {colors['primary']};
            margin-bottom: 1rem;
        }}
        
        /* Testimonials */
        .testimonials {{
            padding: 80px 20px;
            background: #f8f9fa;
        }}
        
        .testimonials-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }}
        
        .testimonial-card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .stars {{
            color: #fbbf24;
            margin-bottom: 1rem;
        }}
        
        .testimonial-text {{
            font-style: italic;
            margin-bottom: 1rem;
            color: #555;
        }}
        
        .testimonial-author {{
            font-weight: 600;
            color: {colors['primary']};
        }}
        
        /* Final CTA */
        .final-cta {{
            padding: 80px 20px;
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%);
            color: white;
            text-align: center;
        }}
        
        .final-cta h2 {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .final-cta p {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        /* Footer */
        footer {{
            background: #2c3e50;
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        
        .contact-info {{
            margin-bottom: 1rem;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 2rem;
            }}
            
            .hero p {{
                font-size: 1.2rem;
            }}
            
            .section-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>{content['hero']['headline']}</h1>
            <p>{content['hero']['subheadline']}</p>
            <div class="cta-buttons">
                <a href="#contact" class="btn btn-primary">{content['hero']['cta_primary']}</a>
                <a href="#services" class="btn btn-secondary">{content['hero']['cta_secondary']}</a>
            </div>
        </div>
    </section>
    
    <!-- Benefits Section -->
    <section class="benefits">
        <div class="container">
            <h2 class="section-title">{content['benefits']['title']}</h2>
            <div class="benefits-grid">
"""
    
    # Add benefits
    for benefit in content['benefits']['items']:
        html += f"""
                <div class="benefit-card">
                    <div class="benefit-icon">{benefit['icon']}</div>
                    <h3>{benefit['title']}</h3>
                    <p>{benefit['description']}</p>
                </div>
"""
    
    html += """
            </div>
        </div>
    </section>
    
    <!-- Services Section -->
    <section class="services" id="services">
        <div class="container">
            <h2 class="section-title">""" + content['services']['title'] + """</h2>
            <div class="services-grid">
"""
    
    # Add services
    for service in content['services']['items']:
        html += f"""
                <div class="service-card">
                    <h3>{service['icon']} {service['name']}</h3>
                    <p>{service['description']}</p>
                </div>
"""
    
    html += """
            </div>
        </div>
    </section>
    
    <!-- Testimonials Section -->
    <section class="testimonials">
        <div class="container">
            <h2 class="section-title">""" + content['testimonials']['title'] + """</h2>
            <div class="testimonials-grid">
"""
    
    # Add testimonials
    for testimonial in content['testimonials']['items']:
        stars = '★' * testimonial['rating']
        html += f"""
                <div class="testimonial-card">
                    <div class="stars">{stars}</div>
                    <p class="testimonial-text">"{testimonial['text']}"</p>
                    <p class="testimonial-author">{testimonial['author']}</p>
                    <p style="color: #888; font-size: 0.9rem;">{testimonial['role']}</p>
                </div>
"""
    
    html += f"""
            </div>
        </div>
    </section>
    
    <!-- Final CTA Section -->
    <section class="final-cta" id="contact">
        <div class="container">
            <h2>{content['cta']['title']}</h2>
            <p>{content['cta']['subtitle']}</p>
            <a href="mailto:{content['contact']['email']}" class="btn btn-primary">{content['cta']['button_text']}</a>
            <p style="margin-top: 1rem; opacity: 0.8;">{content['cta']['subtext']}</p>
        </div>
    </section>
    
    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="contact-info">
                <p>📧 {content['contact']['email']}</p>
                <p>📱 {content['contact']['phone']}</p>
                <p>📍 {content['contact']['address']}</p>
            </div>
            <p style="margin-top: 2rem; opacity: 0.7;">© {datetime.now().year} Todos los derechos reservados</p>
        </div>
    </footer>
</body>
</html>
"""
    
    return html


def save_landing_page(html, business_name, style='modern'):
    """Guarda la landing page como archivo HTML"""
    output_dir = 'landing_pages'
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{business_name.lower().replace(' ', '_')}_{style}_{datetime.now().strftime('%Y%m%d')}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'✅ Landing page guardada: {filepath}')
    return filepath


def main():
    """Demo del Landing Page Builder"""
    print('🏗️ LANDING PAGE BUILDER\n')
    
    # Ejemplo: Consultora de Salud
    business_info = {
        'name': 'HealthConsult Pro',
        'industry': 'consultora de salud',
        'value_prop': 'Transformamos el bienestar de tu organización',
        'services': [
            'Consultas médicas especializadas',
            'Programas de wellness corporativo',
            'Nutrición y coaching de salud',
            'Telemedicina 24/7'
        ],
        'target_audience': 'empresas que cuidan el bienestar de su equipo',
        'contact': {
            'email': 'info@healthconsult.com',
            'phone': '+1 (555) 123-4567',
            'address': 'Miami, FL'
        }
    }
    
    # Generar contenido
    print('📝 Generando contenido...')
    content = generate_landing_page_content(business_info)
    print(f"✅ Contenido generado: {len(content)} secciones\n")
    
    # Generar HTML (3 estilos)
    styles = ['modern', 'minimal', 'corporate']
    
    for style in styles:
        print(f'🎨 Generando landing page estilo: {style}')
        html = generate_landing_page_html(content, style=style)
        filepath = save_landing_page(html, business_info['name'], style=style)
        print(f'📄 Archivo: {filepath}\n')
    
    print('✨ ¡Landing pages generadas!')
    print(f'📁 Carpeta: landing_pages/')
    print('💡 Abre los archivos HTML en tu navegador para verlos')


if __name__ == '__main__':
    main()