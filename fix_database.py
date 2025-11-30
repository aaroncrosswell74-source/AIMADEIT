# fix_database.py (Railway/PostgreSQL version - fully compatible)
import psycopg2
import json
import uuid
from datetime import datetime
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def create_database():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("🛠️ CREATING ARKWELL DATABASE TABLES...")

    # Drop tables if they exist to avoid type conflicts
    cursor.execute("DROP TABLE IF EXISTS user_node_access CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS nodes CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS migrations CASCADE;")
    
    # Users table
    cursor.execute("""
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        email TEXT,
        handle TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    # Nodes table
    cursor.execute("""
    CREATE TABLE nodes (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        label TEXT NOT NULL,
        tier INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        policy JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    
    # User node access table
    cursor.execute("""
    CREATE TABLE user_node_access (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        status TEXT NOT NULL,
        source TEXT NOT NULL,
        granted_by TEXT,
        expires_at TIMESTAMP,
        meta JSONB,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        unlocked INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(node_id) REFERENCES nodes(id)
    );
    """)
    
    # Migrations table
    cursor.execute("""
    CREATE TABLE migrations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TIMESTAMP NOT NULL
    );
    """)
    
    print("🌱 SEEDING ARKWELL DATA...")

    # Seed users
    users = [
        ("MOCK-USER-12345", "operative@arkwell.com", "ArkwellOperative"),
        ("ADMIN.AARON", "aaron@arkwell.com", "DirectorAaron")
    ]
    for uid, email, handle in users:
        cursor.execute("""
        INSERT INTO users (id, email, handle) VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
        """, (uid, email, handle))
    
    # Seed nodes
    nodes = [
        ("RECRUIT", "Arkwell Recruit", 0, {"open": True}),
        ("OPERATIVE", "Field Operative", 1, {"payment": True, "multisig": 0}),
        ("SPECOPS", "Special Operations", 2, {"payment": True, "multisig": 1}),
        ("DIRECTOR", "Command Director", 3, {"payment": True, "multisig": 0})
    ]
    for code, label, tier, policy in nodes:
        cursor.execute("""
        INSERT INTO nodes (id, code, label, tier, policy)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (code) DO NOTHING;
        """, (str(uuid.uuid4()), code, label, tier, json.dumps(policy)))
    
    # Grant RECRUIT access to mock user
    cursor.execute("""
    INSERT INTO user_node_access (id, user_id, node_id, status, source, unlocked)
    SELECT %s, u.id, n.id, 'approved', 'system', 1
    FROM users u, nodes n
    WHERE u.id = 'MOCK-USER-12345' AND n.code = 'RECRUIT'
    ON CONFLICT (id) DO NOTHING;
    """, (str(uuid.uuid4()),))
    
    # Record migration
    cursor.execute("""
    INSERT INTO migrations (id, name, applied_at)
    VALUES (%s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
    """, (str(uuid.uuid4()), "0001_init.sql", datetime.utcnow()))
    
    conn.commit()
    conn.close()
    print("✅ ARKWELL DATABASE CREATED SUCCESSFULLY!")

if __name__ == "__main__":
    create_database()
