import os
import stripe

# ⚠️ PLACEHOLDER KEYS – DO NOT PUSH LIVE KEYS TO GITHUB
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

stripe.api_key = STRIPE_SECRET_KEY

# Placeholder product price IDs
ARKWELL_PRODUCTS = {
    "OPERATIVE": "price_placeholder_1",
    "SPECOPS": "price_placeholder_2",
    "DIRECTOR": "price_placeholder_3"
}
