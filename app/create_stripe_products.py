import stripe
import os

# ⚠️ Use placeholders
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")

def create_products():
    print("🛠️ CREATING ARKWELL STRIPE PRODUCTS (PLACEHOLDER)...")
    
    products = [
        {"name": "ARKWELL Operative", "code": "OPERATIVE", "price": 4900},
        {"name": "ARKWELL SpecOps", "code": "SPECOPS", "price": 14900},
        {"name": "ARKWELL Director", "code": "DIRECTOR", "price": 49900},
    ]

    created_products = {}
    
    for product in products:
        # Just log placeholder
        created_products[product["code"]] = f"price_placeholder_{product['code']}"
        print(f"✅ {product['name']}: price_placeholder_{product['code']}")
    
    print("\n🎯 UPDATE stripe_config.py WITH REAL PRICE IDs WHEN READY")

if __name__ == "__main__":
    create_products()
