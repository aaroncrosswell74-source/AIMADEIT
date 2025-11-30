import os
import logging
from psycopg import connect
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from environment variables.")

# Extract target DB name from DATABASE_URL
TARGET_DB = DATABASE_URL.rsplit("/", 1)[1]

# Build URL that points to default 'postgres' DB
ROOT_DB_URL = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"


def ensure_database_exists():
    """Connect to default DB, check if target DB exists, create if missing."""
    try:
        logger.info(f"[DB] Checking if database '{TARGET_DB}' exists...")

        with connect(ROOT_DB_URL) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s;",
                    (TARGET_DB,)
                )
                exists = cur.fetchone()

                if exists:
                    logger.info(f"[DB] Database '{TARGET_DB}' already exists.")
                else:
                    logger.info(f"[DB] Database '{TARGET_DB}' missing — creating...")
                    cur.execute(f'CREATE DATABASE "{TARGET_DB}";')
                    logger.info(f"[DB] Database '{TARGET_DB}' created successfully.")

    except Exception as e:
        logger.error(f"[DB] Failed during database existence check: {e}")
        raise


# Ensure DB exists before making pool
ensure_database_exists()

# Create global pool to the final DB
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    timeout=5
)


def setup_db_pool():
    logger.info("[DB] PostgreSQL connection pool initialized.")


def get_db_connection():
    return pool.getconn()


def return_db_connection(conn):
    pool.putconn(conn)


def shutdown_db_pool():
    pool.close()
    logger.info("[DB] PostgreSQL pool shut down.")
