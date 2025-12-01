import logging
import os
from flask import Flask, request, jsonify, g, redirect
from flask_cors import CORS

from db_connection import (
    get_db_connection,
    return_db_connection
)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portal_server")

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
MAILERLITE_URL = "https://YOUR_MAILERLITE_URL_HERE"
# Replace the above string with your actual MailerLite landing page URL.

# -------------------------------------------------------
# BEFORE REQUEST — get DB connection
# -------------------------------------------------------
@app.before_request
def before_request():
    try:
        g.db_conn = get_db_connection()
    except Exception as e:
        logger.error(f"[DB] connection error: {e}")
        return jsonify({"error": "database_unavailable"}), 500

# -------------------------------------------------------
# AFTER REQUEST — return connection
# -------------------------------------------------------
@app.teardown_request
def teardown_request(exception):
    conn = getattr(g, "db_conn", None)
    if conn:
        return_db_connection(conn)

# -------------------------------------------------------
# ROOT ROUTE
# -------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "online", "message": "Sovereign Kingdom running"})

# -------------------------------------------------------
# OFFER ROUTES (Redirection to MailerLite)
# -------------------------------------------------------
@app.route("/offer/ai", methods=["GET"])
def offer_ai():
    """Redirects to MailerLite opt-in."""
    return redirect(MAILERLITE_URL, code=302)

@app.route("/offer/saas", methods=["GET"])
def offer_saas():
    """Redirects to MailerLite opt-in."""
    return redirect(MAILERLITE_URL, code=302)

# -------------------------------------------------------
# HEALTHCHECK
# -------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        return_db_connection(conn)
        return jsonify({"database": "ok", "result": result}), 200
    except Exception as e:
        logger.error(f"[HEALTHCHECK ERROR] {e}")
        return jsonify({"database": "error", "details": str(e)}), 500

# -------------------------------------------------------
# ENTRY (Render uses this)
# -------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
