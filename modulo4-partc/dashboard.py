"""
Módulo 4C - Analytics Dashboard
Flask API principal con endpoints REST para métricas y reportes
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from db import db, get_metrics_by_platform, get_platform_comparison
from analytics_engine import AnalyticsEngine
from report_generator import ReportGenerator

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

analytics = AnalyticsEngine()
report_gen = ReportGenerator()


@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'service': 'Analytics Dashboard API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'database': 'PostgreSQL' if db.use_postgresql else 'SQLite'
    })


@app.route('/health')
def health():
    try:
        db.execute_query("SELECT 1")
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/metrics/<platform>', methods=['GET'])
def get_platform_metrics(platform):
    valid_platforms = ['instagram', 'twitter', 'linkedin', 'tiktok', 'youtube']
    if platform not in valid_platforms:
        return jsonify({'error': f'Plataforma inválida. Debe ser: {", ".join(valid_platforms)}'}), 400
    
    limit = request.args.get('limit', 100, type=int)
    days = request.args.get('days', 7, type=int)
    
    try:
        metrics = get_metrics_by_platform(platform, limit)
        
        if metrics:
            total_vistas = sum(m['vistas'] for m in metrics)
            total_likes = sum(m['likes'] for m in metrics)
            total_comentarios = sum(m['comentarios'] for m in metrics)
            avg_engagement = sum(m['engagement_rate'] for m in metrics) / len(metrics)
        else:
            total_vistas = total_likes = total_comentarios = avg_engagement = 0
        
        return jsonify({
            'platform': platform,
            'posts_count': len(metrics),
            'period_days': days,
            'totals': {
                'vistas': total_vistas,
                'likes': total_likes,
                'comentarios': total_comentarios,
                'avg_engagement_rate': round(avg_engagement, 2)
            },
            'posts': metrics
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/compare', methods=['GET'])
def compare_platforms():
    platforms_param = request.args.get('platforms', 'instagram,twitter,linkedin,tiktok,youtube')
    platforms = platforms_param.split(',')
    
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    
    try:
        comparison = get_platform_comparison(start_date, end_date)
        comparison = [c for c in comparison if c['plataforma'] in platforms]
        
        return jsonify({
            'start_date': start_date,
            'end_date': end_date,
            'platforms': platforms,
            'comparison': comparison
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/post/<post_id>', methods=['GET'])
def get_post_metrics(post_id):
    try:
        query = """
            SELECT * FROM metricas_posts
            WHERE post_id = %s
            ORDER BY timestamp DESC
        """ if db.use_postgresql else """
            SELECT * FROM metricas_posts
            WHERE post_id = ?
            ORDER BY timestamp DESC
        """
        
        metrics = db.execute_query(query, (post_id,))
        
        if not metrics:
            return jsonify({'error': 'Post no encontrado'}), 404
        
        return jsonify({
            'post_id': post_id,
            'platform': metrics[0]['plataforma'],
            'metrics_history': metrics
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports', methods=['GET'])
def list_reports():
    try:
        query = "SELECT * FROM reportes_programados ORDER BY created_at DESC"
        reports = db.execute_query(query)
        
        return jsonify({
            'count': len(reports),
            'reports': reports
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports', methods=['POST'])
def create_report():
    data = request.json
    required = ['nombre', 'frecuencia', 'formato']
    if not all(field in data for field in required):
        return jsonify({'error': f'Campos requeridos: {", ".join(required)}'}), 400
    
    try:
        return jsonify({
            'message': 'Reporte creado (TODO: implementar)',
            'data': data
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/<int:report_id>/generate', methods=['GET'])
def generate_report(report_id):
    try:
        return jsonify({
            'message': 'Generación de reporte (TODO: implementar)',
            'report_id': report_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/best-times', methods=['GET'])
def get_best_times():
    platform = request.args.get('platform')
    
    try:
        if platform:
            query = """
                SELECT * FROM mejores_horarios
                WHERE plataforma = %s
                ORDER BY promedio_engagement DESC
                LIMIT 10
            """ if db.use_postgresql else """
                SELECT * FROM mejores_horarios
                WHERE plataforma = ?
                ORDER BY promedio_engagement DESC
                LIMIT 10
            """
            params = (platform,)
        else:
            query = "SELECT * FROM mejores_horarios ORDER BY promedio_engagement DESC LIMIT 20"
            params = None
        
        best_times = db.execute_query(query, params)
        
        return jsonify({
            'platform': platform if platform else 'all',
            'best_times': best_times
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/top-content', methods=['GET'])
def get_top_content():
    platform = request.args.get('platform')
    limit = request.args.get('limit', 10, type=int)
    
    try:
        if platform:
            query = """
                SELECT * FROM metricas_posts
                WHERE plataforma = %s
                ORDER BY engagement_rate DESC
                LIMIT %s
            """ if db.use_postgresql else """
                SELECT * FROM metricas_posts
                WHERE plataforma = ?
                ORDER BY engagement_rate DESC
                LIMIT ?
            """
            params = (platform, limit)
        else:
            query = """
                SELECT * FROM metricas_posts
                ORDER BY engagement_rate DESC
                LIMIT %s
            """ if db.use_postgresql else """
                SELECT * FROM metricas_posts
                ORDER BY engagement_rate DESC
                LIMIT ?
            """
            params = (limit,)
        
        top_posts = db.execute_query(query, params)
        
        return jsonify({
            'platform': platform if platform else 'all',
            'limit': limit,
            'top_posts': top_posts
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    print("\n" + "="*50)
    print("🚀 Analytics Dashboard API")
    print("="*50)
    print(f"📍 Puerto: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"💾 Base de datos: {'PostgreSQL' if db.use_postgresql else 'SQLite'}")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)