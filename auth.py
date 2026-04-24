import os
import functools
from flask import request, jsonify, g
from db import get_db_connection


def require_module(module_name):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'Missing X-API-Key header'}), 401
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT t.id, t.name, t.active, s.modules
                FROM tenants t
                JOIN subscriptions s ON s.tenant_id = t.id
                WHERE t.api_key = %s
                  AND t.active = TRUE
                  AND s.status = 'active'
                LIMIT 1
            """, (api_key,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return jsonify({'error': 'Invalid or inactive API key'}), 403
            tenant_id, tenant_name, _, modules = row
            if module_name not in (modules or []):
                return jsonify({'error': 'Module not in your plan'}), 403
            g.tenant_id = tenant_id
            g.tenant_name = tenant_name
            return f(*args, **kwargs)
        return wrapper
    return decorator


ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', '')


def require_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        admin_key = request.headers.get('X-Admin-Key')
        if not admin_key or admin_key != ADMIN_SECRET_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return wrapper
