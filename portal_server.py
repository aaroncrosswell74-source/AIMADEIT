from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
# NOTE: This is the correct way to import the function from the engine file.
from trideva_engine import execute_canonical_ritual

# --- Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for development environment

# --- MOCK USER STATE ---
MOCK_USER_TIERS = {}
print("[INIT] Mock User Tier Store initialized (in-memory dictionary).")

# --- Configuration ---
CANONICAL_AUTH_KEY = "trideva_sacred_key_555"

# --- Routes ---

@app.route('/')
def home():
    return render_template('trideva_engine_portal_flask.html')

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ONLINE",
        "engine_version": "V3.0.0",
        "timestamp": time.time()
    })

@app.route('/api/user/tier/<user_id>', methods=['GET'])
def get_user_tier(user_id):
    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    return jsonify({"success": True, "ritualTier": ritual_tier, "userId": user_id})

@app.route('/api/discord/grant_tier', methods=['POST'])
def grant_tier_from_discord():
    data = request.json
    if data.get('auth_key') != CANONICAL_AUTH_KEY:
        return jsonify({"success": False, "message": "Unauthorized access key."}), 401

    user_id = data.get('userId')
    tier = data.get('tier', 1)

    if user_id:
        MOCK_USER_TIERS[user_id] = max(MOCK_USER_TIERS.get(user_id, 0), tier)
        app.logger.info(f"[GRANT] User {user_id} granted Tier {tier}. Current: {MOCK_USER_TIERS[user_id]}")
        return jsonify({"success": True, "ritualTier": MOCK_USER_TIERS[user_id]})

    return jsonify({"success": False, "message": "Missing user ID."}), 400

@app.route('/api/ritual', methods=['POST'])
def run_ritual_from_web():
    data = request.json
    user_id = data.get('userId')
    seed_concept = data.get('seedConcept')

    if not user_id or not seed_concept:
        return jsonify({"success": False, "message": "Missing user ID or seed concept."}), 400

    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    if ritual_tier == 0:
        return jsonify({
            "success": False,
            "message": "Tier 0 Access Denied. Initiate the Pass first.",
            "ritualTier": 0
        }), 403

    try:
        app.logger.info(f"[WEB RITUAL] User {user_id} (Tier {ritual_tier}) initiated ritual: {seed_concept[:20]}...")
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

# --- MOCK PAYMENT ENDPOINTS ---
@app.route('/api/stripe/create-checkout-session', methods=['POST'])
def create_stripe_checkout_session():
    data = request.json
    user_id = data.get('userId', 'anonymous')
    MOCK_USER_TIERS[user_id] = 1
    return jsonify({
        "success": True,
        "url": "https://mock-stripe.com/checkout/success",
        "mock_grant": True,
        "userId": user_id
    })

@app.route('/api/hybrid/create-onramp-session', methods=['POST'])
def create_onramp_session():
    data = request.json
    user_id = data.get('userId', 'anonymous')
    MOCK_USER_TIERS[user_id] = 1
    return jsonify({
        "success": True,
        "url": "https://mock-onramp.com/initiate/success",
        "mock_grant": True,
        "userId": user_id
    })

if __name__ == '__main__':
    print("[FLASK] Starting Canonical Portal Server on http://localhost:5000")
    app.run(debug=True, port=5000)
