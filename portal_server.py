from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
# NOTE: This is the correct way to import the function from the engine file.
from trideva_engine import execute_canonical_ritual

# --- Setup ---\
# NOTE: You MUST have your flask template in a subfolder named 'templates'
app = Flask(__name__)
CORS(app)  # Enable CORS for development environment

# --- MOCK USER STATE (Simulates Firestore/Redis for Tier tracking) ---
# In a production environment, this would be a database lookup.
MOCK_USER_TIERS = {}
print("[INIT] Mock User Tier Store initialized (in-memory dictionary).")
# ---------------------------------------------------------------------

# --- Configuration (MUST MATCH DISCORD BOT) ---
CANONICAL_AUTH_KEY = "trideva_sacred_key_555"
# ----------------------------------------------


# --- Routes ---

@app.route('/')
def home():
    """Renders the HTML template (client portal) when the user navigates to the root URL (/)."""
    # The HTML file must be in a subfolder named 'templates'
    return render_template('trideva_engine_portal_flask.html')


@app.route('/api/health')
def health_check():
    """Returns the engine status for the frontend UI."""
    return jsonify({
        "status": "ONLINE",
        "engine_version": "V3.0.0",  # Updated to reflect canonical engine
        "timestamp": time.time()
    })
    

@app.route('/api/user/tier/<user_id>', methods=['GET'])
def get_user_tier(user_id):
    """
    Returns the user's highest canonical tier from the store.
    This is the core security check used by the Discord bot and Web Portal.
    """
    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    
    # Tier 0 is the default un-initiated state.
    return jsonify({"success": True, "ritualTier": ritual_tier, "userId": user_id})


@app.route('/api/discord/grant_tier', methods=['POST'])
def grant_tier_from_discord():
    """
    Endpoint used ONLY by the Discord bot upon successful payment verification.
    Requires the canonical auth key to prevent unauthorized tier grants.
    """
    data = request.json
    
    if data.get('auth_key') != CANONICAL_AUTH_KEY:
        return jsonify({"success": False, "message": "Unauthorized access key."}), 401
        
    user_id = data.get('userId')
    tier = data.get('tier', 1)
    
    if user_id:
        # Update the tier if the incoming tier is higher than the current tier
        MOCK_USER_TIERS[user_id] = max(MOCK_USER_TIERS.get(user_id, 0), tier)
        app.logger.info(f"[GRANT] User {user_id} granted Tier {tier}. Current: {MOCK_USER_TIERS[user_id]}")
        return jsonify({"success": True, "ritualTier": MOCK_USER_TIERS[user_id]})
    
    return jsonify({"success": False, "message": "Missing user ID."}), 400


@app.route('/api/ritual', methods=['POST'])
def run_ritual_from_web():
    """
    Endpoint for the Web Portal to execute the ritual.
    It performs a security check for the user's tier before running the engine.
    """
    data = request.json
    user_id = data.get('userId')
    seed_concept = data.get('seedConcept')
    
    if not user_id or not seed_concept:
        return jsonify({"success": False, "message": "Missing user ID or seed concept."}), 400

    # 1. Get Canonical Tier
    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    
    if ritual_tier == 0:
        return jsonify({
            "success": False, 
            "message": "Tier 0 Access Denied. Initiate the Pass first.", 
            "ritualTier": 0
        }), 403

    # 2. Execute the engine
    try:
        app.logger.info(f"[WEB RITUAL] User {user_id} (Tier {ritual_tier}) initiated ritual: {seed_concept[:20]}...")
        
        # The engine function needs the tier to run the gating logic internally
        result = execute_canonical_ritual(
            initial_seed=seed_concept,
            user_id=user_id,
            ritual_tier=ritual_tier
        )
        
        return jsonify({
            "success": True, 
            "ritualTier": ritual_tier,
            "archetype_id": result.get('archetype_id'),
            "final_seed": result.get('final_seed'),
            "cycles_completed": result.get('cycles_completed'),
            "ritual_results": result.get('ritual_results'),
            "lore_entry": result.get('lore_entry'),
            "lore_description": result.get('lore_description'),
            "card_icon": result.get('card_icon'),
            "card_name": result.get('card_name')
        })

    except Exception as e:
        app.logger.error(f"Ritual execution failed: {e}")
        return jsonify({"success": False, "message": f"Server Error during ritual execution: {str(e)}"}), 500


# --- MOCK PAYMENT ENDPOINTS (For client UI button actions) ---

@app.route('/api/stripe/create-checkout-session', methods=['POST'])
def create_stripe_checkout_session():
    """ Mocks Stripe checkout """
    data = request.json
    user_id = data.get('userId', 'anonymous')
    
    # Grant tier immediately for mock purposes
    MOCK_USER_TIERS[user_id] = 1
    
    return jsonify({
        "success": True, 
        "url": "https://mock-stripe.com/checkout/success",
        "mock_grant": True,
        "userId": user_id
    })

@app.route('/api/hybrid/create-onramp-session', methods=['POST'])
def create_onramp_session():
    """ Mocks Hybrid Fiat-to-Crypto On-Ramp """
    data = request.json
    user_id = data.get('userId', 'anonymous')
    
    # Grant tier immediately for mock purposes
    MOCK_USER_TIERS[user_id] = 1

    return jsonify({
        "success": True, 
        "url": "https://mock-onramp.com/initiate/success",
        "mock_grant": True,
        "userId": user_id
    })


if __name__ == '__main__':
    # Flask needs to run in a sub-thread or separate process for discord.py to work correctly.
    # When running directly, use debug=True for easier development.
    print("[FLASK] Starting Canonical Portal Server on http://localhost:5000")
    app.run(debug=True, port=5000)