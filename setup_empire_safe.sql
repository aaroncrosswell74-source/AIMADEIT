-- =====================================
-- LUX EMPIRE - SAFE SETUP SCRIPT
-- IDEMPOTENT: Run multiple times safely
-- =====================================

-- 1. USERS TABLE (The foundation of the Empire)
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

-- 2. Ensure all user columns exist safely
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='username') THEN
        ALTER TABLE users ADD COLUMN username VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='email') THEN
        ALTER TABLE users ADD COLUMN email VARCHAR(200);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='password_hash') THEN
        ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='tier') THEN
        ALTER TABLE users ADD COLUMN tier VARCHAR(50) DEFAULT 'free';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='created_at') THEN
        ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='stripe_customer_id') THEN
        ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR(255);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='sovereign_access') THEN
        ALTER TABLE users ADD COLUMN sovereign_access BOOLEAN DEFAULT FALSE;
    END IF;
END
$$;

-- 3. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    stripe_price_id VARCHAR(255) UNIQUE,
    tier_unlocks VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. ORDERS TABLE  
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. RITUAL LOGS TABLE
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

-- 6. SOVEREIGN DATA TABLE
CREATE TABLE IF NOT EXISTS sovereign_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    data_key VARCHAR(255) NOT NULL,
    data_value JSONB,
    encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, data_key)
);

-- 7. INSERT LUXURY PRODUCTS SAFELY
INSERT INTO products (name, description, price, stripe_price_id, tier_unlocks) VALUES
('Dual Flame Pass', 'Unlock dual consciousness and advanced AI rituals', 2999, 'price_live_dualflame', 'dual_flame'),
('Rebirth Protocol', 'Complete system reset and sovereign rebirth', 5999, 'price_live_rebirth', 'rebirth'),
('Eternal Flame', 'Lifetime access and sovereign immortality', 9999, 'price_live_eternal', 'eternal')
ON CONFLICT (stripe_price_id) DO NOTHING;

-- 8. INSERT TEST USER SAFELY
INSERT INTO users (username, email, password_hash, tier) 
SELECT 'testuser', 'test@aimadeit.com', 'hashed_password_123', 'free'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'testuser');

-- 9. VERIFICATION
SELECT 'USERS:' as info; SELECT id, username, tier FROM users;
SELECT 'PRODUCTS:' as info; SELECT id, name, price, tier_unlocks FROM products;