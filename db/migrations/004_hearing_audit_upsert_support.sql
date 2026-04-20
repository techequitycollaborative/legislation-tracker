-- =============================================================================
-- Migration: Add constraints, columns and triggers to support upsert + better
--            database auditing
-- Run once against legtracker_2026
-- =============================================================================

BEGIN;

-- Manually delete problematic rows from hearing_bills to be restored later
DELETE FROM snapshot.hearing_bills WHERE id=602;
DELETE FROM snapshot.hearing_bills WHERE id=861;

-- Natural key for hearings: chamber, name, date
ALTER TABLE snapshot.hearings
    ADD CONSTRAINT uq_hearings_chamber_name_date
    UNIQUE(chamber_id, name, date);

-- Natural key for hearing_bills: hearing_id, bill_id
ALTER TABLE snapshot.hearing_bills
    ADD CONSTRAINT uq_hearing_bills_hearing_bill
    UNIQUE(hearing_id, openstates_bill_id);

-- New column for hearings to record cancellation rather than dropping rows
ALTER TABLE snapshot.hearings
    ADD COLUMN canceled_at TIMESTAMPTZ DEFAULT NULL;

-- Trigger function: update hearings.updated_at on meaningful column changes
-- Excludes derived columns (committee_id, chamber_id, created_at)
CREATE OR REPLACE FUNCTION snapshot.update_hearing_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        NEW.time_verbatim       IS DISTINCT FROM OLD.time_verbatim OR
        NEW.time_normalized     IS DISTINCT FROM OLD.time_normalized OR
        NEW.is_allday           IS DISTINCT FROM OLD.is_allday OR
        NEW.location            IS DISTINCT FROM OLD.location OR
        NEW.room                IS DISTINCT FROM OLD.room OR
        NEW.notes               IS DISTINCT FROM OLD.notes OR
        NEW.canceled_at         IS DISTINCT FROM OLD.canceled_at
    ) THEN
        NEW.updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trg_hearings_updated_at
BEFORE UPDATE ON snapshot.hearings
FOR EACH ROW EXECUTE FUNCTION snapshot.update_hearing_updated_at();


-- Trigger function: update hearings.updated_at when any child hearing_bills row
-- is inserted, updated, or deleted
-- COALESCE handles the null NEW (on DELETE) and null OLD (on INSERT) cases
CREATE OR REPLACE FUNCTION snapshot.touch_hearing_on_bill_change()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE snapshot.hearings
    SET updated_at = CURRENT_TIMESTAMP
    WHERE hearing_id = COALESCE(NEW.hearing_id, OLD.hearing_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 
CREATE TRIGGER trg_hearing_bills_touch_parent
AFTER INSERT OR UPDATE OR DELETE ON snapshot.hearing_bills
FOR EACH ROW EXECUTE FUNCTION snapshot.touch_hearing_on_bill_change();

COMMIT;

-- =============================================================================
-- NOTE: This migration intentionally does NOT backfill tokens.
-- Run scripts/generate_tokens.py after applying this migration.
-- That script prints raw tokens to stdout (once) and stores only the hash here.
-- =============================================================================