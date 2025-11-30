# create_stripe_products.py
import stripe

# Use your LIVE keys from above
stripe.api_key = "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"

def create_products():
    print("🛠️ CREATING ARKWELL STRIPE PRODUCTS...")
    
    products = [
        {"name": "ARKWELL Operative", "code": "OPERATIVE", "price": 4900},  # $49
        {"name": "ARKWELL SpecOps", "code": "SPECOPS", "price": 14900},     # $149  
        {"name": "ARKWELL Director", "code": "DIRECTOR", "price": 49900},   # $499
    ]

    created_products = {}
    
    for product in products:
        try:
            # Create product
            stripe_product = stripe.Product.create(
                name=product["name"],
                description=f"ARKWELL {product['code']} Tier Access"
            )
            
            # Create price
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=product["price"],
                currency="usd",
                recurring={"interval": "month"},
            )
            
            created_products[product["code"]] = stripe_price.id
            print(f"✅ {product['name']}: {stripe_price.id}")
            
        except Exception as e:
            print(f"❌ Failed to create {product['name']}: {e}")
    
    print("\n🎯 UPDATE YOUR stripe_config.py WITH THESE PRICE IDs:")
    for code, price_id in created_products.items():
        print(f'{code}: "{price_id}"')

if __name__ == "__main__":
    create_products()