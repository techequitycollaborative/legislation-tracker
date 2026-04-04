-- =============================================================================
-- Migration: Add iCal feed token columns to auth tables
-- Run once against legtracker_2026
-- =============================================================================

BEGIN;

-- Users 
ALTER TABLE auth.approved_users
    ADD COLUMN IF NOT EXISTS feed_token_hash TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS feed_token_created_at TIMESTAMPTZ;

-- Organizations 
ALTER TABLE auth.approved_organizations
    ADD COLUMN IF NOT EXISTS feed_token_hash TEXT UNIQUE,
    ADD COLUMN IF NOT EXISTS feed_token_created_at TIMESTAMPTZ;

-- Indexes for fast token lookups (hash compared on every request) 
CREATE INDEX IF NOT EXISTS idx_approved_users_feed_token
    ON auth.approved_users (feed_token_hash)
    WHERE feed_token_hash IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_approved_orgs_feed_token
    ON auth.approved_organizations (feed_token_hash)
    WHERE feed_token_hash IS NOT NULL;

COMMIT;

-- =============================================================================
-- NOTE: This migration intentionally does NOT backfill tokens.
-- Run scripts/generate_tokens.py after applying this migration.
-- That script prints raw tokens to stdout (once) and stores only the hash here.
-- =============================================================================