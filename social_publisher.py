"""
Modulo 4B - Social Publisher
Publica contenido programado en redes sociales
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from db import get_connection
from auth import require_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

social_bp = Blueprint('social', __name__)


# ── Endpoints de publicacion ──────────────────────────────────────────────────

@social_bp.route('/api/v1/social/posts', methods=['GET'])
@require_module('social_publisher')
def get_posts():
    """Lista publicaciones del tenant"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        estado = request.args.get('estado')
        plataforma = request.args.get('plataforma')

        query = """
            SELECT id, plataforma, contenido, estado, fecha_publicacion,
                   fecha_programada, error_mensaje, created_at
            FROM social_posts
            WHERE tenant_id = %s
        """
        params = [g.tenant_id]

        if estado:
            query += " AND estado = %s"
            params.append(estado)
        if plataforma:
            query += " AND plataforma = %s"
            params.append(plataforma)

        query += " ORDER BY created_at DESC LIMIT 50"
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()

        posts = []
        for r in rows:
            posts.append({
                'id': r[0],
                'plataforma': r[1],
                'contenido': r[2],
                'estado': r[3],
                'fecha_publicacion': str(r[4]) if r[4] else None,
                'fecha_programada': str(r[5]) if r[5] else None,
                'error_mensaje': r[6],
                'created_at': str(r[7])
            })

        return jsonify({'success': True, 'posts': posts, 'total': len(posts)})
    finally:
        conn.close()


@social_bp.route('/api/v1/social/posts', methods=['POST'])
@require_module('social_publisher')
def create_post():
    """Crea una nueva publicacion programada"""
    data = request.get_json()
    plataforma = data.get('plataforma')
    contenido = data.get('contenido')
    fecha_programada = data.get('fecha_programada')
    imagen_url = data.get('imagen_url')

    if not plataforma or not contenido:
        return jsonify({'error': 'plataforma y contenido son requeridos'}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO social_posts
                (tenant_id, plataforma, contenido, estado, fecha_programada, imagen_url)
            VALUES (%s, %s, %s, 'programado', %s, %s)
            RETURNING id
        """, (g.tenant_id, plataforma, contenido, fecha_programada, imagen_url))
        post_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        logger.info(f"Post {post_id} creado para tenant {g.tenant_id} en {plataforma}")
        return jsonify({'success': True, 'post_id': post_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@social_bp.route('/api/v1/social/posts/<int:post_id>/publish', methods=['POST'])
@require_module('social_publisher')
def publish_post(post_id):
    """Publica inmediatamente un post programado"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT plataforma, contenido, imagen_url
            FROM social_posts
            WHERE id = %s AND tenant_id = %s
        """, (post_id, g.tenant_id))
        row = cur.fetchone()

        if not row:
            return jsonify({'error': 'Post no encontrado'}), 404

        plataforma, contenido, imagen_url = row

        # Intentar publicar segun la plataforma
        resultado = _publicar_en_plataforma(
            plataforma, contenido, imagen_url, g.tenant_id, conn
        )

        if resultado['success']:
            cur.execute("""
                UPDATE social_posts
                SET estado = 'publicado', fecha_publicacion = NOW()
                WHERE id = %s
            """, (post_id,))
            _log_publicacion(conn, post_id, plataforma, 'publicado',
                            'Publicado exitosamente', resultado)
        else:
            cur.execute("""
                UPDATE social_posts
                SET estado = 'error', error_mensaje = %s
                WHERE id = %s
            """, (resultado.get('error', 'Error desconocido'), post_id))
            _log_publicacion(conn, post_id, plataforma, 'error',
                            resultado.get('error'), resultado)
            # Registrar en errores
            cur.execute("""
                INSERT INTO errores_publicacion (publicacion_id, plataforma, error)
                VALUES (%s, %s, %s)
            """, (post_id, plataforma, resultado.get('error', 'Error desconocido')))

        conn.commit()
        cur.close()
        return jsonify(resultado)
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@social_bp.route('/api/v1/social/posts/<int:post_id>', methods=['DELETE'])
@require_module('social_publisher')
def delete_post(post_id):
    """Elimina un post programado (solo si no fue publicado)"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM social_posts
            WHERE id = %s AND tenant_id = %s AND estado != 'publicado'
        """, (post_id, g.tenant_id))
        deleted = cur.rowcount
        conn.commit()
        cur.close()

        if deleted == 0:
            return jsonify({'error': 'Post no encontrado o ya publicado'}), 404
        return jsonify({'success': True, 'message': f'Post {post_id} eliminado'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@social_bp.route('/api/v1/social/tokens', methods=['POST'])
@require_module('social_publisher')
def save_token():
    """Guarda o actualiza token de API de una plataforma"""
    data = request.get_json()
    plataforma = data.get('plataforma')
    access_token = data.get('access_token')

    if not plataforma or not access_token:
        return jsonify({'error': 'plataforma y access_token requeridos'}), 400

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_tokens (plataforma, access_token, account_id, metadata)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (plataforma)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                account_id = EXCLUDED.account_id,
                updated_at = NOW()
        """, (plataforma, access_token,
              data.get('account_id'), json.dumps(data.get('metadata', {}))))
        conn.commit()
        cur.close()
        return jsonify({'success': True, 'plataforma': plataforma}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@social_bp.route('/api/v1/social/stats', methods=['GET'])
@require_module('social_publisher')
def get_stats():
    """Estadisticas de publicaciones del tenant"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) FILTER (WHERE estado = 'publicado') as publicados,
                COUNT(*) FILTER (WHERE estado = 'programado') as programados,
                COUNT(*) FILTER (WHERE estado = 'error') as errores,
                COUNT(*) as total
            FROM social_posts
            WHERE tenant_id = %s
        """, (g.tenant_id,))
        row = cur.fetchone()
        cur.close()

        return jsonify({
            'success': True,
            'stats': {
                'publicados': row[0],
                'programados': row[1],
                'errores': row[2],
                'total': row[3]
            }
        })
    finally:
        conn.close()


# ── Helpers privados ──────────────────────────────────────────────────────────

def _publicar_en_plataforma(plataforma, contenido, imagen_url, tenant_id, conn):
    """Intenta publicar en la plataforma indicada usando el token guardado"""
    cur = conn.cursor()
    cur.execute(
        "SELECT access_token, account_id FROM api_tokens WHERE plataforma = %s",
        (plataforma,)
    )
    token_row = cur.fetchone()
    cur.close()

    if not token_row:
        return {
            'success': False,
            'error': f'No hay token configurado para {plataforma}'
        }

    access_token, account_id = token_row

    # Aqui se integran las APIs reales de cada plataforma
    # Por ahora simulamos la publicacion exitosa
    logger.info(f"Publicando en {plataforma} para tenant {tenant_id}")

    # TODO: Integrar APIs reales:
    # - Instagram: Graph API
    # - TikTok: TikTok API
    # - LinkedIn: LinkedIn API
    # - X/Twitter: Twitter API v2

    return {
        'success': True,
        'plataforma': plataforma,
        'post_id_externo': f'sim_{plataforma}_{datetime.now().timestamp():.0f}',
        'mensaje': f'Publicado exitosamente en {plataforma}'
    }


def _log_publicacion(conn, post_id, plataforma, accion, mensaje, response_data):
    """Registra una accion en los logs de publicacion"""
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs_publicacion (publicacion_id, plataforma, accion, mensaje, response_data)
        VALUES (%s, %s, %s, %s, %s)
    """, (post_id, plataforma, accion, mensaje, json.dumps(response_data)))
    cur.close()
