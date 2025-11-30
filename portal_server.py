from dotenv import load_dotenv
import os
import logging
import uuid
import time

from flask import Flask, jsonify, request, g, abort, render_template
from flask_cors import CORS

# Database connection helpers (PostgreSQL)
from db_connection import (
    setup_db_pool,
    get_db_connection,
    return_db_connection,
    shutdown_db_pool,
)

# Trideva Engine
from trideva_engine import execute_canonical_ritual

# Load environment variables from .env (for local dev; on Render, env vars come from dashboard)
load_dotenv()

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app)  # Enable CORS for web/JS access

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Trideva Engine State / Config ---

# In-memory mock tier store (can be replaced with DB-backed tiers later)
MOCK_USER_TIERS: dict[str, int] = {}
logger.info("[INIT] Mock User Tier Store initialized (in-memory dictionary).")

# Shared secret for Discord → Portal tier grants
CANONICAL_AUTH_KEY = "trideva_sacred_key_555"

# --- Database Setup and Teardown ---


@app.before_request
def before_request():
    """
    Acquire a database connection from the pool and store it in Flask's 'g' object.
    This ensures the connection is available for the duration of the request.
    """
    try:
        if not hasattr(g, "db_conn"):
            g.db_conn = get_db_connection()
    except RuntimeError as e:
        logger.error(f"Failed to acquire database connection: {e}")
        abort(503, description="Database service unavailable.")


@app.teardown_request
def teardown_request(exception=None):
    """
    Return the database connection to the pool after the request is finished.
    """
    conn = g.pop("db_conn", None)
    if conn is not None:
        return_db_connection(conn)


# --- PostgreSQL Data Access Functions ---


def get_product_details(product_id: int):
    """
    Fetches details for a single product from the PostgreSQL 'products' table.
    """
    conn = g.db_conn
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "SELECT id, name, price, description FROM products WHERE id = %s;"
        cursor.execute(sql, (product_id,))
        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "price": float(row[2]),
                "description": row[3],
            }
        return None

    except Exception as e:
        conn.rollback()
        logger.error(f"Error fetching product {product_id}: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


def get_user_by_username(username: str):
    """
    Fetches user data by username for authentication.

    Assumes 'users' table has columns: id, username, hashed_password, tier.
    """
    conn = g.db_conn
    cursor = None
    user_data = None
    try:
        cursor = conn.cursor()
        sql = """
        SELECT id, username, hashed_password, tier
        FROM users
        WHERE username = %s;
        """
        cursor.execute(sql, (username,))
        row = cursor.fetchone()

        if row:
            user_data = {
                "id": row[0],
                "username": row[1],
                "hashed_password": row[2],
                "tier": row[3],
            }

    except Exception as e:
        conn.rollback()
        logger.error(f"Error fetching user {username}: {e}")
    finally:
        if cursor:
            cursor.close()

    return user_data


def create_new_user(username: str, hashed_password: str, tier: str = "none") -> int | None:
    """
    Inserts a new user and returns the new user's ID.
    """
    conn = g.db_conn
    cursor = None
    new_user_id = None

    try:
        cursor = conn.cursor()
        sql = """
        INSERT INTO users (username, hashed_password, tier)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        cursor.execute(sql, (username, hashed_password, tier))
        conn.commit()
        new_user_id = cursor.fetchone()[0]

    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating user {username}: {e}")
        new_user_id = None
    finally:
        if cursor:
            cursor.close()

    return new_user_id


# --- Core Portal Routes (Postgres-backed) ---


@app.route("/product/<int:product_id>", methods=["GET"])
def product_view(product_id: int):
    product = get_product_details(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route("/auth/login", methods=["POST"])
def login_user():
    """
    Basic login route placeholder using PostgreSQL.
    NOTE: Password verification is a placeholder; real app must hash + verify.
    """
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")  # plaintext from user

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = get_user_by_username(username)
    if user:
        # TODO: verify password hash properly here
        return jsonify(
            {
                "message": "Login successful (password check skipped)",
                "user_id": user["id"],
                "tier": user["tier"],
            }
        )

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/auth/register", methods=["POST"])
def register_user():
    """
    Handles user registration using PostgreSQL.
    """
    data = request.json or {}
    username = data.get("username")
    password_hash = data.get("password_hash", str(uuid.uuid4()))  # placeholder

    if not username or not password_hash:
        return jsonify({"error": "Missing required fields"}), 400

    if get_user_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    new_id = create_new_user(username, password_hash)

    if new_id:
        return jsonify(
            {
                "message": "User registered successfully",
                "user_id": new_id,
                "username": username,
            }
        ), 201

    return jsonify({"error": "Failed to create user due to a database issue"}), 500


# --- Trideva Portal + Engine Routes ---


@app.route("/")
def home():
    """
    Renders the Trideva Engine portal HTML.
    templates/trideva_engine_portal_flask.html
    """
    return render_template("trideva_engine_portal_flask.html")


@app.route("/api/health")
def health_check():
    """
    Health endpoint for status checks.
    """
    return jsonify(
        {
            "status": "ONLINE",
            "engine_version": "V3.0.0",
            "timestamp": time.time(),
        }
    )


@app.route("/api/user/tier/<user_id>", methods=["GET"])
def get_user_tier(user_id: str):
    """
    Returns the user's highest canonical tier from the (mock) store.
    """
    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    return jsonify({"success": True, "ritualTier": ritual_tier, "userId": user_id})


@app.route("/api/discord/grant_tier", methods=["POST"])
def grant_tier_from_discord():
    """
    Endpoint used ONLY by the Discord bot upon successful payment verification.
    Requires the canonical auth key to prevent unauthorized tier grants.
    """
    data = request.json or {}

    if data.get("auth_key") != CANONICAL_AUTH_KEY:
        return jsonify({"success": False, "message": "Unauthorized access key."}), 401

    user_id = data.get("userId")
    tier = data.get("tier", 1)

    if user_id:
        MOCK_USER_TIERS[user_id] = max(MOCK_USER_TIERS.get(user_id, 0), tier)
        app.logger.info(
            f"[GRANT] User {user_id} granted Tier {tier}. Current: {MOCK_USER_TIERS[user_id]}"
        )
        return jsonify({"success": True, "ritualTier": MOCK_USER_TIERS[user_id]})

    return jsonify({"success": False, "message": "Missing user ID."}), 400


@app.route("/api/ritual", methods=["POST"])
def run_ritual_from_web():
    """
    Web Portal endpoint to execute the Trideva ritual.
    Performs a tier check before calling the engine.
    """
    data = request.json or {}
    user_id = data.get("userId")
    seed_concept = data.get("seedConcept")

    if not user_id or not seed_concept:
        return jsonify({"success": False, "message": "Missing user ID or seed concept."}), 400

    ritual_tier = MOCK_USER_TIERS.get(user_id, 0)
    if ritual_tier == 0:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Tier 0 Access Denied. Initiate the Pass first.",
                    "ritualTier": 0,
                }
            ),
            403,
        )

    try:
        app.logger.info(
            f"[WEB RITUAL] User {user_id} (Tier {ritual_tier}) initiated ritual: {seed_concept[:20]}..."
        )

        result = execute_canonical_ritual(
            initial_seed=seed_concept,
            user_id=user_id,
            ritual_tier=ritual_tier,
        )

        return jsonify(
            {
                "success": True,
                "ritualTier": ritual_tier,
                "archetype_id": result.get("archetype_id"),
                "final_seed": result.get("final_seed"),
                "cycles_completed": result.get("cycles_completed"),
                "ritual_results": result.get("ritual_results"),
                "lore_entry": result.get("lore_entry"),
                "lore_description": result.get("lore_description"),
                "card_icon": result.get("card_icon"),
                "card_name": result.get("card_name"),
            }
        )

    except Exception as e:
        app.logger.error(f"Ritual execution failed: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Server Error during ritual execution: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/stripe/create-checkout-session", methods=["POST"])
def create_stripe_checkout_session():
    """
    MOCK Stripe checkout endpoint.
    Grants tier 1 immediately for demo purposes.
    """
    data = request.json or {}
    user_id = data.get("userId", "anonymous")

    MOCK_USER_TIERS[user_id] = max(MOCK_USER_TIERS.get(user_id, 0), 1)

    return jsonify(
        {
            "success": True,
            "url": "https://mock-stripe.com/checkout/success",
            "mock_grant": True,
            "userId": user_id,
        }
    )


@app.route("/api/hybrid/create-onramp-session", methods=["POST"])
def create_onramp_session():
    """
    MOCK Hybrid Fiat-to-Crypto on-ramp endpoint.
    Grants tier 1 immediately for demo purposes.
    """
    data = request.json or {}
    user_id = data.get("userId", "anonymous")

    MOCK_USER_TIERS[user_id] = max(MOCK_USER_TIERS.get(user_id, 0), 1)

    return jsonify(
        {
            "success": True,
            "url": "https://mock-onramp.com/initiate/success",
            "mock_grant": True,
            "userId": user_id,
        }
    )


# --- Local Dev Entry Point (Render uses gunicorn) ---


if __name__ == "__main__":
    try:
        setup_db_pool()
        logger.info("Application starting with PostgreSQL Connection Pool + Trideva Engine.")
        print("[FLASK] Starting Canonical Portal Server on http://localhost:5000")
        app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
    except Exception as e:
        logger.critical(f"Fatal error during application startup: {e}")
        shutdown_db_pool()
