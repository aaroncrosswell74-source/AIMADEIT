# fix_database.py
import sqlite3
import json
import uuid
from datetime import datetime

def create_database():
    conn = sqlite3.connect('sovereign_kingdom.db')
    cursor = conn.cursor()
    
    print("🛠️ CREATING ARKWELL DATABASE TABLES...")
    
    # Create tables
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT,
        handle TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        label TEXT NOT NULL,
        tier INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        policy TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_node_access (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        status TEXT NOT NULL,
        source TEXT NOT NULL,
        granted_by TEXT,
        expires_at TIMESTAMP,
        meta TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        unlocked INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(node_id) REFERENCES nodes(id)
    );

    CREATE TABLE IF NOT EXISTS migrations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TEXT NOT NULL
    );
    """)
    
    # Seed data
    print("🌱 SEEDING ARKWELL DATA...")
    
    # Users
    cursor.execute("INSERT OR IGNORE INTO users (id, email, handle) VALUES (?, ?, ?)",
                   ("MOCK-USER-12345", "operative@arkwell.com", "ArkwellOperative"))
    cursor.execute("INSERT OR IGNORE INTO users (id, email, handle) VALUES (?, ?, ?)", 
                   ("ADMIN.AARON", "aaron@arkwell.com", "DirectorAaron"))
    
    # Nodes
    nodes = [
        ("RECRUIT", "Arkwell Recruit", 0, '{"open": true}'),
        ("OPERATIVE", "Field Operative", 1, '{"payment": true, "multisig": 0}'),
        ("SPECOPS", "Special Operations", 2, '{"payment": true, "multisig": 1}'),
        ("DIRECTOR", "Command Director", 3, '{"payment": true, "multisig": 0}')
    ]
    
    for code, label, tier, policy in nodes:
        cursor.execute("INSERT OR IGNORE INTO nodes (id, code, label, tier, policy) VALUES (?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), code, label, tier, policy))
    
    # Grant access
    cursor.execute("""
        INSERT OR IGNORE INTO user_node_access (id, user_id, node_id, status, source, unlocked)
        SELECT ?, u.id, n.id, 'approved', 'system', 1
        FROM users u, nodes n 
        WHERE u.id = 'MOCK-USER-12345' AND n.code = 'RECRUIT'
    """, (str(uuid.uuid4()),))
    
    # Record migration
    cursor.execute("INSERT OR IGNORE INTO migrations (id, name, applied_at) VALUES (?, ?, ?)",
                   (str(uuid.uuid4()), "0001_init.sql", datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()
    print("✅ ARKWELL DATABASE CREATED SUCCESSFULLY!")

if __name__ == "__main__":
    create_database()