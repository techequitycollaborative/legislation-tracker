-- =============================================================================
-- Migration: Alter constraint on hearings since a committee can meet more than
--            once on the same date
-- Run once against legtracker_2026
-- =============================================================================

BEGIN;

-- Drop old uniqueness constraint
ALTER TABLE snapshot.hearings
    DROP CONSTRAINT uq_hearings_chamber_name_date;

-- Add new uniqueness constraint
ALTER TABLE snapshot.hearings
    ADD CONSTRAINT uq_hearings_chamber_name_date_time
    UNIQUE (chamber_id, name, date, time_verbatim);
COMMIT;

-- =============================================================================
-- -- ROLLBACK
-- BEGIN;
-- ALTER TABLE snapshot.hearings
--     DROP CONSTRAINT uq_hearings_chamber_name_date_time;

-- ALTER TABLE snapshot.hearings
--     ADD CONSTRAINT uq_hearings_chamber_name_date
--     UNIQUE (chamber_id, name, date);
-- COMMIT;
-- =============================================================================