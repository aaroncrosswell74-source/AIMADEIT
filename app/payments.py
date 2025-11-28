# app/payments.py
from fastapi import APIRouter, Request, HTTPException, Header
import stripe
from app.stripe_config import STRIPE_WEBHOOK_SECRET, ARKWELL_PRODUCTS
from app.db import get_pool
from app.logger import logger
import json

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-checkout-session")
async def create_checkout_session(node_code: str, user_id: str = "MOCK-USER-12345"):
    """Create Stripe checkout session for ARKWELL tier access"""
    try:
        if node_code not in ARKWELL_PRODUCTS:
            raise HTTPException(400, "Invalid node code")
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': ARKWELL_PRODUCTS[node_code],
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:8000/payments/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:8000/payments/cancel',
            client_reference_id=user_id,
            metadata={
                'node_code': node_code,
                'user_id': user_id
            }
        )
        
        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}
        
    except Exception as e:
        logger.error(f"Stripe session error: {e}")
        raise HTTPException(500, str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Handle Stripe webhook events - GRANT ACCESS ON PAYMENT"""
    payload = await request.body()
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(400, "Invalid signature")
    
    # Handle payment success
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_payment_success(session)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription)
    
    return {"status": "success"}

async def handle_payment_success(session):
    """Grant access when payment is successful"""
    db = get_pool()
    user_id = session['client_reference_id']
    node_code = session['metadata']['node_code']
    
    logger.info(f"🎉 PAYMENT SUCCESS: {user_id} purchased {node_code}")
    
    # Grant access in database
    await db.execute("""
        INSERT INTO user_node_access (id, user_id, node_id, status, source, unlocked, meta)
        SELECT ?, ?, nodes.id, 'approved', 'stripe_payment', 1, ?
        FROM nodes WHERE nodes.code = ?
    """, (
        f"stripe_{session['id']}",
        user_id,
        json.dumps({"stripe_session_id": session['id'], "subscription_id": session.get('subscription')}),
        node_code
    ))
    
    logger.info(f"✅ ACCESS GRANTED: {user_id} → {node_code}")

async def handle_subscription_cancelled(subscription):
    """Handle subscription cancellation"""
    db = get_pool()
    
    # Find and revoke access
    await db.execute("""
        UPDATE user_node_access 
        SET status = 'expired', unlocked = 0, updated_at = datetime('now')
        WHERE meta LIKE ? AND status = 'approved'
    """, f'%{subscription["id"]}%')
    
    logger.info(f"🔒 ACCESS REVOKED: Subscription {subscription['id']} cancelled")

@router.get("/success")
async def payment_success(session_id: str):
    """Payment success page"""
    return {
        "status": "success", 
        "message": "Welcome to ARKWELL! Your access has been granted.",
        "session_id": session_id
    }

@router.get("/cancel")
async def payment_cancel():
    """Payment cancellation page"""
    return {"status": "cancelled", "message": "Payment was cancelled"}