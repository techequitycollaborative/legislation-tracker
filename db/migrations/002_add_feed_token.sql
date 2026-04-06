-- =============================================================================
-- Migration: Add plaintext feed token columns to auth tables
-- Run after 001_add_feed_tokens.sql
-- =============================================================================

BEGIN;

ALTER TABLE auth.approved_users
    ADD COLUMN IF NOT EXISTS feed_token TEXT;

ALTER TABLE auth.approved_organizations
    ADD COLUMN IF NOT EXISTS feed_token TEXT;

COMMIT;

-- =============================================================================
-- NOTE: Existing feed_token_hash values are unaffected.
-- Run python -m db.admin.backfill_tokens --regenerate after applying this
-- migration to populate feed_token for all existing users and orgs.
-- =============================================================================