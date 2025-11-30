import os
import time
import logging
from psycopg import connect, OperationalError
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from environment variables.")

# Extract the target db from the URL
TARGET_DB = DATABASE_URL.rsplit("/", 1)[1]

# Root DB = same URL but ending in /postgres
ROOT_DB_URL = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"


def wait_for_postgres(retries=10, delay=2):
    """Retry until PostgreSQL server is ready."""
    for i in range(retries):
        try:
            logger.info(f"[DB] Attempt {i+1}: Checking PostgreSQL availability...")
            with connect(ROOT_DB_URL) as conn:
                logger.info("[DB] PostgreSQL is online.")
                return True
        except OperationalError as e:
            logger.warning(f"[DB] Postgres not ready yet: {e}")
            time.sleep(delay)

    raise RuntimeError("PostgreSQL did not become ready in time.")


def ensure_database_exists():
    """Ensure the target DB exists; create if missing."""
    try:
        logger.info(f"[DB] Ensuring database '{TARGET_DB}' exists...")

        with connect(ROOT_DB_URL) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (TARGET_DB,))
                if cur.fetchone():
                    logger.info(f"[DB] Database '{TARGET_DB}' already exists.")
                else:
                    logger.info(f"[DB] Creating database '{TARGET_DB}'...")
                    cur.execute(f'CREATE DATABASE "{TARGET_DB}";')
                    logger.info(f"[DB] Database '{TARGET_DB}' created successfully.")

    except Exception as e:
        logger.error(f"[DB] Failed during database creation check: {e}")
        raise


# NEW: Wait for Railway to finish provisioning the DB
wait_for_postgres()

# NEW: Create DB only after server is definitely online
ensure_database_exists()

# Create pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    timeout=10
)


def get_db_connection():
    return pool.getconn()


def return_db_connection(conn):
    pool.putconn(conn)
