# app/stripe_config.py - UPDATED WITH REAL PRICE IDs
import os
import stripe

# 🚀 LIVE STRIPE KEYS
STRIPE_SECRET_KEY = "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"
STRIPE_PUBLISHABLE_KEY = "pk_live_51SGoNsR05AlbGpIjICMBtpt5r8f7Ob0RL7HOTxBfHqWvLLQ1Xo4w07bOF5cYQpWRKW8y2UsD2VNw4yxz4F7ycnnk00UcSZ2NNv"
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret_here")

stripe.api_key = STRIPE_SECRET_KEY

# 🎯 REAL ARKWELL PRICE IDs (FROM YOUR OUTPUT)
ARKWELL_PRODUCTS = {
    "OPERATIVE": "price_1SYQu5R05AlbGpIj2FGXUeel",  # $49/month
    "SPECOPS": "price_1SYQu5R05AlbGpIjm8P9N5ne",    # $149/month  
    "DIRECTOR": "price_1SYQu5R05AlbGpIj96hq7SGn"    # $499/month
}