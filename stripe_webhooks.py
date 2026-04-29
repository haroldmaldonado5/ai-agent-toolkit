"""
Modulo - Stripe Billing Webhooks
Maneja eventos de Stripe para actualizar planes automaticamente
"""
import os
import json
import stripe
from flask import Blueprint, request, jsonify
from db import get_connection

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

stripe_bp = Blueprint('stripe', __name__)

PRICE_TO_PLAN = {
    # Reemplaza con tus Price IDs de Stripe
    # 'price_starter_id': 'starter',
    # 'price_pro_id': 'pro',
    # 'price_enterprise_id': 'enterprise',
}

PLAN_MODULES = {
    'starter': ['reporting'],
    'pro': ['reporting', 'followup', 'leads', 'social_scheduler'],
    'enterprise': ['reporting', 'followup', 'leads', 'social_scheduler',
                   'social_publisher', 'analytics']
}


@stripe_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            event = json.loads(payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    event_type = event.get('type')

    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(event['data']['object'])
    elif event_type == 'customer.subscription.updated':
        _handle_subscription_updated(event['data']['object'])
    elif event_type == 'customer.subscription.deleted':
        _handle_subscription_cancelled(event['data']['object'])
    elif event_type == 'invoice.payment_failed':
        _handle_payment_failed(event['data']['object'])

    return jsonify({'received': True}), 200


@stripe_bp.route('/api/billing/create-checkout', methods=['POST'])
def create_checkout():
    """Crea sesion de checkout de Stripe para un tenant"""
    data = request.get_json()
    plan = data.get('plan', 'pro')
    tenant_email = data.get('email')
    tenant_id = data.get('tenant_id')

    price_ids = {
        'starter': os.environ.get('STRIPE_PRICE_STARTER'),
        'pro': os.environ.get('STRIPE_PRICE_PRO'),
        'enterprise': os.environ.get('STRIPE_PRICE_ENTERPRISE'),
    }
    price_id = price_ids.get(plan)

    if not price_id:
        return jsonify({'error': f'Price ID no configurado para plan {plan}'}), 400

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            customer_email=tenant_email,
            metadata={'tenant_id': str(tenant_id), 'plan': plan},
            success_url='https://ai-agent-toolkit-production.up.railway.app/billing/success',
            cancel_url='https://ai-agent-toolkit-production.up.railway.app/billing/cancel',
        )
        return jsonify({'checkout_url': session.url, 'session_id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stripe_bp.route('/billing/success')
def billing_success():
    return jsonify({'status': 'success', 'message': 'Suscripcion activada exitosamente'})


@stripe_bp.route('/billing/cancel')
def billing_cancel():
    return jsonify({'status': 'cancelled', 'message': 'Checkout cancelado'})


# ── Handlers privados ─────────────────────────────────────────────────────────

def _handle_checkout_completed(session):
    tenant_id = session.get('metadata', {}).get('tenant_id')
    plan = session.get('metadata', {}).get('plan', 'pro')
    stripe_id = session.get('subscription')

    if not tenant_id:
        return

    modules = PLAN_MODULES.get(plan, ['reporting'])
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE tenants SET plan = %s WHERE id = %s", (plan, tenant_id))
        cur.execute("""
            UPDATE subscriptions
            SET plan = %s, modules = %s, stripe_id = %s, status = 'active'
            WHERE tenant_id = %s
        """, (plan, json.dumps(modules), stripe_id, tenant_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()


def _handle_subscription_updated(subscription):
    stripe_id = subscription.get('id')
    status = subscription.get('status')
    price_id = subscription['items']['data'][0]['price']['id'] if subscription.get('items') else None
    plan = PRICE_TO_PLAN.get(price_id, 'pro')
    modules = PLAN_MODULES.get(plan, ['reporting'])

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE subscriptions
            SET plan = %s, modules = %s, status = %s
            WHERE stripe_id = %s
        """, (plan, json.dumps(modules), status, stripe_id))
        conn.commit()
        cur.close()
    finally:
        conn.close()


def _handle_subscription_cancelled(subscription):
    stripe_id = subscription.get('id')
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE subscriptions SET status = 'cancelled' WHERE stripe_id = %s
        """, (stripe_id,))
        cur.execute("""
            UPDATE tenants SET active = FALSE
            WHERE id = (SELECT tenant_id FROM subscriptions WHERE stripe_id = %s)
        """, (stripe_id,))
        conn.commit()
        cur.close()
    finally:
        conn.close()


def _handle_payment_failed(invoice):
    stripe_id = invoice.get('subscription')
    if not stripe_id:
        return
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE subscriptions SET status = 'past_due' WHERE stripe_id = %s
        """, (stripe_id,))
        conn.commit()
        cur.close()
    finally:
        conn.close()
