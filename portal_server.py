import os
import logging
from flask import Flask, jsonify, request, g
from flask_cors import CORS

# Updated import — no setup_db_pool
from db_connection import (
    get_db_connection,
    return_db_connection,
    shutdown_db_pool,
)

from trideva_engine import TridevaEngine
from routes import register_routes

logger = logging.getLogger("portal_server")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Initialize the Trideva Engine once
engine = TridevaEngine()


@app.before_request
def before_request():
    """Open DB connection for the request."""
    try:
        g.db_conn = get_db_connection()
    except Exception as e:
        logger.error(f"[DB] Failed to acquire connection from pool: {e}")
        return jsonify({"error": "Database unavailable"}), 500


@app.teardown_request
def teardown_request(exception=None):
    """Release DB connection back to the pool."""
    conn = getattr(g, "db_conn", None)
    if conn:
        return_db_connection(conn)


# Register all API routes
register_routes(app, engine)


@app.route("/")
def root():
    return jsonify({"message": "Sovereign Kingdom Portal is live."})


# Simplified startup block — no setup_db_pool
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[FLASK] Starting Canonical Portal Server on http://localhost:{port}")
    app.run(debug=True, port=port)
