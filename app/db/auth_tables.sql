-- auth_tables.sql
-- Create all tables for leg tracker authentication mechanism.

-- Table: approved_users
CREATE TABLE IF NOT EXISTS approved_users (
    approved_user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    org_name VARCHAR(100),
    user_role VARCHAR(20) CHECK (
        user_role IN ('admin', 'basic', 'custom')
    )
);


-- Table: organizations
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    domain TEXT
);

-- Table: logged_users
CREATE TABLE IF NOT EXISTS logged_users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    password_hash TEXT,
    org_id INTEGER NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

