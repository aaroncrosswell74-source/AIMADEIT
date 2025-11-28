# In Meena's db.py - minimal changes
from persistence import SovereignSQLite

_sqlite_db = None

async def setup_db_pool():
    global _sqlite_db
    _sqlite_db = SovereignSQLite()
    return _sqlite_db

def get_pool():
    global _sqlite_db
    if not _sqlite_db:
        raise RuntimeError("Database not initialized")
    return _sqlite_db