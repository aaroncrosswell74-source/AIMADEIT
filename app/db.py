import os
import asyncpg
from app.persistence import logger

_pg_pool: Optional[asyncpg.pool.Pool] = None

async def setup_db_pool():
    global _pg_pool
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        _pg_pool = await asyncpg.create_pool(dsn=db_url)
        logger.info("[Postgres] Connection pool initialized")
        return _pg_pool
    else:
        # fallback to SQLite
        return await setup_sqlite_pool()

def get_pool():
    if _pg_pool:
        return _pg_pool
    else:
        raise RuntimeError("Database not initialized. Call setup_db_pool() first.")

async def shutdown_db_pool():
    global _pg_pool
    if _pg_pool:
        await _pg_pool.close()
        logger.info("[Postgres] Connection pool shutdown")
        _pg_pool = None
