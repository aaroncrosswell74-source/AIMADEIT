import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing from environment.")

# Mask password for logging
try:
    user_pass, rest = DATABASE_URL.split("@", 1)
    masked = user_pass.split(":", 1)[0] + ":***@" + rest
except Exception:
    masked = "***"

logger.info(f"[DB] Using URL: {masked}")

# -------------------------------------------------
# TEMPORARY FIX: DISABLE DATABASE CONNECTION POOL
# -------------------------------------------------

connection_pool = None
logger.warning("[DB] Connection pool DISABLED for boot testing.")

def get_db_connection():
    """TEMPORARY: DB disabled so the app can boot safely."""
    raise RuntimeError("Database connection temporarily disabled for boot testing.")

def return_db_connection(conn):
    """TEMPORARILY DISABLED: No-op."""
    pass
