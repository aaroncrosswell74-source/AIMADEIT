import os
import logging
from psycopg import Connection
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from environment variables.")

# Create a global connection pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    timeout=5
)

def setup_db_pool():
    logger.info("[DB] PostgreSQL connection pool initialized.")

def get_db_connection() -> Connection:
    return pool.getconn()

def return_db_connection(conn: Connection):
    pool.putconn(conn)

def shutdown_db_pool():
    pool.close()
    logger.info("[DB] PostgreSQL pool shut down.")
