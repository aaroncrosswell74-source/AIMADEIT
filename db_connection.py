import os
import logging
import psycopg2
from psycopg2 import pool
import urllib.parse as urlparse
import time

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing from environment.")

# Mask password for logs
try:
    user_pass, rest = DATABASE_URL.split("@", 1)
    masked = user_pass.split(":", 1)[0] + ":***@" + rest
except Exception:
    masked = "***"

logger.info(f"[DB] Using URL: {masked}")

# ---------------------------
# LAZY CONNECTION POOL (SAFE)
# ---------------------------

connection_pool = None

def init_pool():
    """Initialize the pool only when first needed, not at import time."""
    global connection_pool
    if connection_pool is not None:
        return connection_pool

    # Parse SSL mode
    params = urlparse.urlparse(DATABASE_URL)
    query_params = urlparse.parse_qs(params.query)
    sslmode = query_params.get("sslmode", ["require"])[0]

    # Retry logic
    for attempt in range(5):
        try:
            logger.info(f"[DB] Initializing pool (attempt {attempt + 1}/5)...")
            connection_pool = pool.SimpleConnectionPool(
                1,
                5,
                DATABASE_URL,
                sslmode=sslmode
            )
            logger.info("[DB] Connection pool initialized successfully.")
            return connection_pool

        except Exception as e:
            logger.warning(f"[DB] Pool init failed: {e}")
            time.sleep(2)

    raise RuntimeError("Could not initialize DB connection pool after retries.")

def get_db_connection():
    """Get a DB connection from the pool, init pool lazily."""
    cp = init_pool()
    return cp.getconn()

def return_db_connection(conn):
    """Return connection to pool."""
    if connection_pool:
        connection_pool.putconn(conn)
