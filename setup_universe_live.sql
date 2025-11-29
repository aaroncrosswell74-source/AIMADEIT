-- =========================
-- MASTER UNIVERSE SETUP + STARTER CONTENT  
-- =========================

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(200) UNIQUE,
    password_hash VARCHAR(255),
    tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    stripe_customer_id VARCHAR(255),
    sovereign_access BOOLEAN DEFAULT FALSE
);

-- 2. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    stripe_price_id VARCHAR(255) UNIQUE,
    tier_unlocks VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. RITUAL LOGS
CREATE TABLE IF NOT EXISTS ritual_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    ritual_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. SOVEREIGN DATA
CREATE TABLE IF NOT EXISTS sovereign_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data_key VARCHAR(255) NOT NULL,
    data_value JSONB,
    encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, data_key)
);

-- 6. CHARACTERS
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    level INTEGER DEFAULT 1,
    attributes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. ITEMS
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    rarity VARCHAR(50),
    owner_id INTEGER REFERENCES users(id)
);

-- 8. FACTIONS
CREATE TABLE IF NOT EXISTS factions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE,
    leader_id INTEGER REFERENCES users(id)
);

-- 9. INSERT DEFAULT PRODUCTS
INSERT INTO products (name, description, price, stripe_price_id, tier_unlocks) VALUES
('Dual Flame Pass','Unlock dual consciousness',2999,'price_live_dualflame','dual_flame'),
('Rebirth Protocol','Complete system reset',5999,'price_live_rebirth','rebirth'),
('Eternal Flame','Lifetime access',9999,'price_live_eternal','eternal')
ON CONFLICT (stripe_price_id) DO NOTHING;

-- 10. INSERT TEST USER
INSERT INTO users (username,email,password_hash,tier) 
SELECT 'testuser','test@aimadeit.com','hashed_password_123','free'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username='testuser');

-- 11. INSERT STARTER CHARACTERS
INSERT INTO characters (user_id,name,level,attributes)
SELECT u.id,'Aether Knight',1,'{"strength":5,"intelligence":4,"agility":3}'
FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

INSERT INTO characters (user_id,name,level,attributes)
SELECT u.id,'Chronomancer',1,'{"strength":2,"intelligence":6,"agility":3}'
FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

-- 12. INSERT STARTER ITEMS
INSERT INTO items (name,description,rarity,owner_id)
SELECT 'Flame Sword','A sword imbued with dual flames','rare',u.id
FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

INSERT INTO items (name,description,rarity,owner_id)
SELECT 'Time Amulet','Manipulates minor temporal events','epic',u.id
FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

-- 13. INSERT STARTER FACTIONS
INSERT INTO factions (name,leader_id)
SELECT 'Order of the Eternal Flame', u.id FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

INSERT INTO factions (name,leader_id)
SELECT 'Chrono Syndicate', u.id FROM users u
WHERE u.username='testuser'
ON CONFLICT DO NOTHING;

-- 14. FINAL VERIFICATION
SELECT '🎉 UNIVERSE DEPLOYED SUCCESSFULLY!' as message;
SELECT 'USERS:' as info; SELECT id, username, tier FROM users;
SELECT 'PRODUCTS:' as info; SELECT id, name, price, tier_unlocks FROM products;
SELECT 'CHARACTERS:' as info; SELECT id, name, level FROM characters;
SELECT 'ITEMS:' as info; SELECT id, name, rarity FROM items;
SELECT 'FACTIONS:' as info; SELECT id, name FROM factions;

\q