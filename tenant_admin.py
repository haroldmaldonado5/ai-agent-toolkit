import os
import secrets
from flask import Blueprint, request, jsonify
from db import get_connection
from auth import require_admin

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/tenants', methods=['GET'])
@require_admin
def list_tenants():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.id, t.name, t.email, t.plan, t.active, t.created_at,
               s.modules, s.status
        FROM tenants t
        LEFT JOIN subscriptions s ON s.tenant_id = t.id
        ORDER BY t.created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tenants = []
    for r in rows:
        tenants.append({
            'id': r[0], 'name': r[1], 'email': r[2],
            'plan': r[3], 'active': r[4], 'created_at': str(r[5]),
            'modules': r[6], 'subscription_status': r[7]
        })
    return jsonify(tenants)


@admin_bp.route('/admin/tenants', methods=['POST'])
@require_admin
def create_tenant():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    plan = data.get('plan', 'starter')

    plan_modules = {
        'starter': ['reporting'],
        'pro': ['reporting', 'followup', 'leads', 'social_scheduler'],
        'enterprise': ['reporting', 'followup', 'leads', 'social_scheduler',
                       'social_publisher', 'analytics']
    }
    modules = plan_modules.get(plan, ['reporting'])
    api_key = secrets.token_hex(32)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tenants (name, email, api_key, plan)
        VALUES (%s, %s, %s, %s) RETURNING id
    """, (name, email, api_key, plan))
    tenant_id = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO subscriptions (tenant_id, plan, modules, status)
        VALUES (%s, %s, %s::jsonb, 'active')
    """, (tenant_id, plan, str(modules).replace("'", '"')))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        'id': tenant_id,
        'name': name,
        'email': email,
        'plan': plan,
        'modules': modules,
        'api_key': api_key
    }), 201


@admin_bp.route('/admin/tenants/<int:tenant_id>', methods=['PATCH'])
@require_admin
def update_tenant(tenant_id):
    data = request.get_json()
    plan = data.get('plan')
    active = data.get('active')

    conn = get_db_connection()
    cur = conn.cursor()

    if plan:
        plan_modules = {
            'starter': ['reporting'],
            'pro': ['reporting', 'followup', 'leads', 'social_scheduler'],
            'enterprise': ['reporting', 'followup', 'leads', 'social_scheduler',
                           'social_publisher', 'analytics']
        }
        modules = plan_modules.get(plan, ['reporting'])
        cur.execute("UPDATE tenants SET plan = %s WHERE id = %s", (plan, tenant_id))
        cur.execute("""
            UPDATE subscriptions SET plan = %s, modules = %s::jsonb
            WHERE tenant_id = %s
        """, (plan, str(modules).replace("'", '"'), tenant_id))

    if active is not None:
        cur.execute("UPDATE tenants SET active = %s WHERE id = %s", (active, tenant_id))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'updated', 'tenant_id': tenant_id})


@admin_bp.route('/admin/tenants/<int:tenant_id>', methods=['DELETE'])
@require_admin
def deactivate_tenant(tenant_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tenants SET active = FALSE WHERE id = %s", (tenant_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'deactivated', 'tenant_id': tenant_id})
