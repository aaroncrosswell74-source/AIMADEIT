import os
import logging
from psycopg import connect
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

RAW_URL = os.getenv("DATABASE_URL")
if not RAW_URL:
    raise RuntimeError("DATABASE_URL missing from environment.")

# Force SSL mode cleanly, regardless of how Render encodes it
if "sslmode" not in RAW_URL:
    DATABASE_URL = RAW_URL + "?sslmode=require"
else:
    DATABASE_URL = RAW_URL

logger.info(f"[DB] Final connection URL: {DATABASE_URL}")

# Create pool with sslmode forced
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=5,
    timeout=10
)

def get_db_connection():
    return pool.getconn()

def return_db_connection(conn):
    pool.putconn(conn)
