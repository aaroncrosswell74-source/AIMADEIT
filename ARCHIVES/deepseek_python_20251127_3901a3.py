# -*- coding: utf-8 -*-
"""Updated Database Interface - SQLite Backend

Replaces Meena's mock with persistent SQLite storage.
Maintains identical interface for drop-in replacement.
"""

from app.persistence import setup_db_pool, get_pool, shutdown_db_pool

# Re-export the exact same interface
__all__ = ['setup_db_pool', 'get_pool', 'shutdown_db_pool']