import os
import logging
from typing import Optional, Any
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Global variable to hold the connection pool instance (Postgres only)
_postgres_pool: Optional[Any] = None

# Define PostgreSQL pool size
MIN_CONN = 1
MAX_CONN = 10

# --- Determine DATABASE_URL ---
DATABASE_URL = os.environ.get("DATABASE_URL")

# Fallback to local SQLite if DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///sovereign_kingdom.db"
    os.environ["DATABASE_URL"] = DATABASE_URL
    logger.info("Using local SQLite database for development.")

# --- Detect if SQLite or PostgreSQL ---
IS_SQLITE = DATABASE_URL.startswith("sqlite://")

if not IS_SQLITE:
    # PostgreSQL-specific imports
    import psycopg2
    import psycopg2.pool

# ----------------- Connection Pool Setup -----------------
def setup_db_pool():
    global _postgres_pool

    if IS_SQLITE:
        # SQLite does not need a pool; return None
        return None

    if _postgres_pool is None:
        try:
            url = urlparse(DATABASE_URL)
            _postgres_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=MIN_CONN,
                maxconn=MAX_CONN,
                host=url.hostname,
                port=url.port,
                database=url.path[1:],  # remove leading '/'
                user=url.username,
                password=url.password
            )
            logger.info(f"[PostgreSQL] Connection Pool initialized (Min: {MIN_CONN}, Max: {MAX_CONN}).")
        except psycopg2.Error as e:
            logger.critical(f"[PostgreSQL] Connection Pool initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize PostgreSQL Connection Pool: {e}")

    return _postgres_pool

# ----------------- Get Connection -----------------
def get_db_connection():
    if IS_SQLITE:
        import sqlite3
        conn = sqlite3.connect("sovereign_kingdom.db")
        conn.row_factory = sqlite3.Row
        return conn

    # PostgreSQL path
    global _postgres_pool
    if _postgres_pool is None:
        setup_db_pool()

    if _postgres_pool is None:
        raise RuntimeError("PostgreSQL connection pool is not established.")

    try:
        conn = _postgres_pool.getconn()
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        logger.error(f"[PostgreSQL] Failed to get connection from pool: {e}")
        raise RuntimeError(f"Could not acquire connection: {e}")

# ----------------- Return Connection -----------------
def return_db_connection(conn: Any):
    if IS_SQLITE:
        if conn:
            conn.close()
        return

    global _postgres_pool
    if _postgres_pool is not None and conn is not None:
        _postgres_pool.putconn(conn)

# ----------------- Shutdown Pool -----------------
def shutdown_db_pool():
    if IS_SQLITE:
        return

    global _postgres_pool
    if _postgres_pool is not None:
        try:
            _postgres_pool.closeall()
            logger.info("[PostgreSQL] Connection Pool closed.")
        except psycopg2.Error as e:
            logger.error(f"[PostgreSQL] Error closing pool connections: {e}")
        finally:
            _postgres_pool = None
