-- =============================================================================
-- Migration: Add footnotes to hearing_bills to better represent hearing info
-- Run once against legtracker_2026
-- =============================================================================

BEGIN;

-- New column for hearing_bills to record special footnotes
ALTER TABLE snapshot.hearing_bills
    ADD COLUMN footnote TEXT DEFAULT NULL;
    ADD COLUMN footnote_symbol CHAR(1) DEFAULT NULL;

COMMIT;

-- =============================================================================
-- ROLLBACK
-- ALTER TABLE snapshot.hearing_bills DROP COLUMN IF EXISTS footnote;
-- =============================================================================