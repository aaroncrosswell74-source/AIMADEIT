# -*- coding: utf-8 -*-
"""Sovereign SQLite Persistence Layer

Drop-in replacement for Meena's mock database.
Provides permanent storage with identical interface.
"""

import sqlite3
import json
import uuid
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Dict, List, Optional, AsyncGenerator
import os

class SovereignSQLite:
    """Production-grade SQLite persistence with async compatibility"""
    
    def __init__(self, db_path: str = "sovereign_kingdom.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_tables()
        self._seed_initial_data()
    
    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
    
    def _init_tables(self):
        """Initialize the sovereign schema - YOUR EXACT DESIGN"""
        with self._sync_connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    handle TEXT UNIQUE,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Nodes table (the sacred gates)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    label TEXT NOT NULL,
                    tier INTEGER NOT NULL DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    policy JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Access spine - your brilliant design
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_node_access (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT NOT NULL,
                    granted_by TEXT,
                    expires_at TIMESTAMP,
                    meta JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unlocked BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (node_id) REFERENCES nodes (id)
                )
            """)
            
            # Multisig approvals
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_node_approvals (
                    id TEXT PRIMARY KEY,
                    access_id TEXT NOT NULL,
                    approver_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (access_id) REFERENCES user_node_access (id),
                    FOREIGN KEY (approver_id) REFERENCES users (id)
                )
            """)
            
            # Payment proofs
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_proofs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    reference TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    meta JSON,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (node_id) REFERENCES nodes (id)
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_user_node ON user_node_access(user_id, node_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_access_status ON user_node_access(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_approvals_access ON user_node_approvals(access_id)")
    
    def _seed_initial_data(self):
        """Seed the sacred nodes and initial users"""
        with self._sync_connection() as conn:
            # Check if we already have nodes to avoid re-seeding
            existing = conn.execute("SELECT COUNT(*) as count FROM nodes").fetchone()
            if existing['count'] > 0:
                return
            
            print("[SQLite] Seeding sovereign nodes...")
            
            # Create initial users
            users = [
                ('MOCK-USER-12345', 'sovereign@trideva.com', 'SovereignInitiate'),
                ('ADMIN.AARON', 'aaron@trideva.com', 'Aaron'),
                ('ADMIN.ELYSIA', 'elysia@trideva.com', 'Elysia')
            ]
            
            for user_id, email, handle in users:
                conn.execute(
                    "INSERT OR IGNORE INTO users (id, email, handle) VALUES (?, ?, ?)",
                    (user_id, email, handle)
                )
            
            # Plant the 9 mythic nodes
            sacred_nodes = [
                {
                    'id': str(uuid.uuid4()),
                    'code': 'COLLAPSE',
                    'label': 'The Collapse',
                    'tier': 0,
                    'policy': json.dumps({'open': True})
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'ENGINE.CORE',
                    'label': 'Trideva Engine Core', 
                    'tier': 3,
                    'policy': json.dumps({
                        'requires': ['pull_mode'],
                        'dependency_check': True,
                        'multisig': 0
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'GLYPH.FORGE',
                    'label': 'Glyph Forge',
                    'tier': 2,
                    'policy': json.dumps({
                        'ritual': True,
                        'requires': ['glyph'],
                        'multisig': 1,
                        'roles': ['Aaron', 'Elysia']
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'PAYMENT.GATE',
                    'label': 'Sovereign Treasury',
                    'tier': 1, 
                    'policy': json.dumps({
                        'payment': True,
                        'multisig': 0
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'REVELATION.1',
                    'label': 'First Revelation',
                    'tier': 1,
                    'policy': json.dumps({
                        'ritual': True,
                        'requires': ['initiation'],
                        'multisig': 0
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'REVELATION.2',
                    'label': 'Second Revelation',
                    'tier': 2,
                    'policy': json.dumps({
                        'requires': ['revelation_1_complete'],
                        'multisig': 1
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'DAEMON.CHANNEL', 
                    'label': 'Daemon Communication',
                    'tier': 2,
                    'policy': json.dumps({
                        'requires': ['engine_access'],
                        'multisig': 0
                    })
                },
                {
                    'id': str(uuid.uuid4()),
                    'code': 'APEX',
                    'label': 'The Apex',
                    'tier': 3,
                    'policy': json.dumps({
                        'requires': ['all_revelations'],
                        'multisig': 2,
                        'roles': ['Aaron', 'Elysia', 'Council'],
                        'council_vote': True
                    })
                }
            ]
            
            for node in sacred_nodes:
                conn.execute(
                    "INSERT INTO nodes (id, code, label, tier, policy) VALUES (?, ?, ?, ?, ?)",
                    (node['id'], node['code'], node['label'], node['tier'], node['policy'])
                )
            
            # Grant initial access to COLLAPSE for the mock user
            conn.execute("""
                INSERT INTO user_node_access 
                (id, user_id, node_id, status, source, unlocked)
                VALUES (?, ?, (SELECT id FROM nodes WHERE code = 'COLLAPSE'), 'approved', 'system', TRUE)
            """, (str(uuid.uuid4()), 'MOCK-USER-12345'))
    
    @contextmanager
    def _sync_connection(self) -> sqlite3.Connection:
        """Sync connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # --- ASYNC COMPATIBLE INTERFACE (Matches Meena's mock exactly) ---
    
    async def fetchrow(self, query: str, *params) -> Optional[Dict[str, Any]]:
        """Execute query and return single row - async compatible"""
        def sync_fetch():
            with self._sync_connection() as conn:
                result = conn.execute(query, params).fetchone()
                return dict(result) if result else None
        
        return await asyncio.get_event_loop().run_in_executor(None, sync_fetch)
    
    async def fetch(self, query: str, *params) -> List[Dict[str, Any]]:
        """Execute query and return all rows - async compatible"""
        def sync_fetch():
            with self._sync_connection() as conn:
                return [dict(row) for row in conn.execute(query, params).fetchall()]
        
        return await asyncio.get_event_loop().run_in_executor(None, sync_fetch)
    
    async def execute(self, query: str, *params) -> None:
        """Execute command - async compatible"""
        def sync_execute():
            with self._sync_connection() as conn:
                conn.execute(query, params)
        
        await asyncio.get_event_loop().run_in_executor(None, sync_execute)
    
    async def fetchval(self, query: str, *params) -> Any:
        """Execute query and return single value - async compatible"""
        def sync_fetchval():
            with self._sync_connection() as conn:
                result = conn.execute(query, params).fetchone()
                return result[0] if result else None
        
        return await asyncio.get_event_loop().run_in_executor(None, sync_fetchval)
    
    # --- MOCK-COMPATIBLE METHODS FOR MEENA'S CODE ---
    
    async def acquire(self):
        """Mock pool acquisition - returns self for context manager"""
        return self
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# Global instance
_sqlite_instance: Optional[SovereignSQLite] = None

async def setup_db_pool():
    """Initialize the SQLite database - replaces Meena's mock setup"""
    global _sqlite_instance
    _sqlite_instance = SovereignSQLite()
    print(f"[SQLite] Sovereign database initialized at {_sqlite_instance.db_path}")
    return _sqlite_instance

def get_pool():
    """Get database pool - identical interface to Meena's mock"""
    global _sqlite_instance
    if not _sqlite_instance:
        raise RuntimeError("Database not initialized. Call setup_db_pool() first.")
    return _sqlite_instance

async def shutdown_db_pool():
    """Clean shutdown - maintains interface compatibility"""
    global _sqlite_instance
    _sqlite_instance = None
    print("[SQLite] Database pool shutdown")