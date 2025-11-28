# persistence.py - Drops into Meena's architecture seamlessly
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class SovereignSQLite:
    def __init__(self, db_path="sovereign_kingdom.db"):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Your exact schema, brought to life"""
        with self.connection() as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    handle TEXT UNIQUE, 
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Nodes table (the sacred gates)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    label TEXT NOT NULL,
                    tier INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
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
                    FOREIGN KEY (node_id) REFERENCES nodes (id),
                    UNIQUE (user_id, node_id)
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
                    currency TEXT DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    meta JSON,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (node_id) REFERENCES nodes (id)
                )
            """)
            
            # Seed the sacred nodes
            self._seed_initial_nodes(conn)
    
    def _seed_initial_nodes(self, conn):
        """Plant the 9 mythic nodes of the Trideva lattice"""
        sacred_nodes = [
            {
                'id': 'node_collapse', 
                'code': 'COLLAPSE', 
                'label': 'The Collapse',
                'tier': 0,
                'policy': json.dumps({'open': True})
            },
            {
                'id': 'node_engine', 
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
                'id': 'node_glyph',
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
                'id': 'node_payment',
                'code': 'PAYMENT.GATE',
                'label': 'Sovereign Treasury',
                'tier': 1,
                'policy': json.dumps({
                    'payment': True,
                    'multisig': 0
                })
            },
            {
                'id': 'node_revelation_1',
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
                'id': 'node_revelation_2', 
                'code': 'REVELATION.2',
                'label': 'Second Revelation',
                'tier': 2,
                'policy': json.dumps({
                    'requires': ['revelation_1_complete'],
                    'multisig': 1
                })
            },
            {
                'id': 'node_daemon',
                'code': 'DAEMON.CHANNEL',
                'label': 'Daemon Communication',
                'tier': 2,
                'policy': json.dumps({
                    'requires': ['engine_access'],
                    'multisig': 0
                })
            },
            {
                'id': 'node_apex',
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
            conn.execute("""
                INSERT OR IGNORE INTO nodes (id, code, label, tier, policy)
                VALUES (?, ?, ?, ?, ?)
            """, (node['id'], node['code'], node['label'], node['tier'], node['policy']))
    
    @contextmanager
    def connection(self):
        """Clean connection management"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # Mock-compatible interface - drops into Meena's code
    async def fetchrow(self, query, *params):
        with self.connection() as conn:
            result = conn.execute(query, params).fetchone()
            return dict(result) if result else None
    
    async def fetch(self, query, *params):
        with self.connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]
    
    async def execute(self, query, *params):
        with self.connection() as conn:
            conn.execute(query, params)
    
    async def fetchval(self, query, *params):
        with self.connection() as conn:
            result = conn.execute(query, params).fetchone()
            return result[0] if result else None