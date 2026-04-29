"""
Modulo 4C - Analytics Dashboard
Consolida metricas de todos los modulos para el tenant
"""
import json
from flask import Blueprint, jsonify, g
from db import get_connection
from auth import require_module

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/v1/analytics/dashboard', methods=['GET'])
@require_module('analytics')
def get_dashboard():
    """Retorna metricas consolidadas de todos los modulos"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        tenant_id = g.tenant_id

        # ── Leads ──────────────────────────────────────────────────────────
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'nuevo') as nuevos,
                COUNT(*) FILTER (WHERE estado = 'contactado') as contactados,
                COUNT(*) FILTER (WHERE estado = 'convertido') as convertidos,
                COUNT(*) FILTER (WHERE estado = 'perdido') as perdidos,
                COALESCE(AVG(score), 0) as score_promedio
            FROM leads
            WHERE tenant_id = %s OR tenant_id IS NULL
        """, (tenant_id,))
        leads = cur.fetchone()

        # ── Social Posts ───────────────────────────────────────────────────
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE estado = 'publicado') as publicados,
                COUNT(*) FILTER (WHERE estado = 'programado') as programados,
                COUNT(*) FILTER (WHERE estado = 'error') as errores
            FROM social_posts
            WHERE tenant_id = %s
        """, (tenant_id,))
        social = cur.fetchone()

        # ── Social por plataforma ──────────────────────────────────────────
        cur.execute("""
            SELECT plataforma, COUNT(*) as total,
                   COUNT(*) FILTER (WHERE estado = 'publicado') as publicados
            FROM social_posts
            WHERE tenant_id = %s
            GROUP BY plataforma
        """, (tenant_id,))
        plataformas = [
            {'plataforma': r[0], 'total': r[1], 'publicados': r[2]}
            for r in cur.fetchall()
        ]

        # ── Leads por dia (ultimos 7 dias) ─────────────────────────────────
        cur.execute("""
            SELECT DATE(fecha_captura) as dia, COUNT(*) as cantidad
            FROM leads
            WHERE fecha_captura >= NOW() - INTERVAL '7 days'
              AND (tenant_id = %s OR tenant_id IS NULL)
            GROUP BY dia
            ORDER BY dia ASC
        """, (tenant_id,))
        leads_por_dia = [
            {'dia': str(r[0]), 'cantidad': r[1]}
            for r in cur.fetchall()
        ]

        # ── Errores recientes ──────────────────────────────────────────────
        cur.execute("""
            SELECT plataforma, COUNT(*) as total
            FROM errores_publicacion
            WHERE resuelto = FALSE
            GROUP BY plataforma
        """)
        errores = [
            {'plataforma': r[0], 'total': r[1]}
            for r in cur.fetchall()
        ]

        cur.close()

        return jsonify({
            'success': True,
            'tenant_id': tenant_id,
            'leads': {
                'total': leads[0],
                'nuevos': leads[1],
                'contactados': leads[2],
                'convertidos': leads[3],
                'perdidos': leads[4],
                'score_promedio': round(float(leads[5]), 1),
                'tasa_conversion': round(
                    (leads[3] / leads[0] * 100) if leads[0] > 0 else 0, 1
                )
            },
            'social': {
                'total': social[0],
                'publicados': social[1],
                'programados': social[2],
                'errores': social[3],
                'por_plataforma': plataformas
            },
            'tendencia': {
                'leads_por_dia': leads_por_dia
            },
            'alertas': {
                'errores_publicacion': errores
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@analytics_bp.route('/api/v1/analytics/leads', methods=['GET'])
@require_module('analytics')
def get_leads_analytics():
    """Analisis detallado de leads"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        tenant_id = g.tenant_id

        cur.execute("""
            SELECT
                estado,
                COUNT(*) as cantidad,
                COALESCE(AVG(score), 0) as score_promedio,
                MIN(fecha_captura) as primer_lead,
                MAX(fecha_captura) as ultimo_lead
            FROM leads
            WHERE tenant_id = %s OR tenant_id IS NULL
            GROUP BY estado
            ORDER BY cantidad DESC
        """, (tenant_id,))

        por_estado = []
        for r in cur.fetchall():
            por_estado.append({
                'estado': r[0],
                'cantidad': r[1],
                'score_promedio': round(float(r[2]), 1),
                'primer_lead': str(r[3]) if r[3] else None,
                'ultimo_lead': str(r[4]) if r[4] else None
            })

        cur.execute("""
            SELECT fuente, COUNT(*) as cantidad
            FROM leads
            WHERE tenant_id = %s OR tenant_id IS NULL
            GROUP BY fuente
            ORDER BY cantidad DESC
        """, (tenant_id,))
        por_fuente = [{'fuente': r[0], 'cantidad': r[1]} for r in cur.fetchall()]

        cur.close()
        return jsonify({
            'success': True,
            'por_estado': por_estado,
            'por_fuente': por_fuente
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@analytics_bp.route('/api/v1/analytics/social', methods=['GET'])
@require_module('analytics')
def get_social_analytics():
    """Analisis detallado de publicaciones sociales"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        tenant_id = g.tenant_id

        cur.execute("""
            SELECT
                plataforma,
                estado,
                COUNT(*) as cantidad,
                MIN(created_at) as primera,
                MAX(created_at) as ultima
            FROM social_posts
            WHERE tenant_id = %s
            GROUP BY plataforma, estado
            ORDER BY plataforma, estado
        """, (tenant_id,))

        resultado = {}
        for r in cur.fetchall():
            plataforma = r[0]
            if plataforma not in resultado:
                resultado[plataforma] = {}
            resultado[plataforma][r[1]] = {
                'cantidad': r[2],
                'primera': str(r[3]) if r[3] else None,
                'ultima': str(r[4]) if r[4] else None
            }

        cur.close()
        return jsonify({'success': True, 'por_plataforma': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
