-- =============================================================================
-- Migration: Refactor app.hearing_bills_mv to reference snapshot.bill
-- Run once against legtracker_2026
-- Views affected: app.hearing_bills_mv
-- =============================================================================

BEGIN;
DROP MATERIALIZED VIEW IF EXISTS app.hearing_bills_mv;
CREATE MATERIALIZED VIEW app.hearing_bills_mv AS

-- Process bill sponsors to get primary author and coauthors
WITH bill_authors AS (
    SELECT 
        openstates_bill_id,
        MAX(CASE WHEN primary_author = 'True' THEN full_name END)               AS author,
        STRING_AGG(CASE WHEN primary_author = 'False' THEN full_name END, ', ') AS coauthors
    FROM snapshot.bill_sponsor
    GROUP BY openstates_bill_id
)

SELECT
    hb.hearing_id,
    hb.openstates_bill_id,
    hb.file_order,
    hb.footnote,
    hb.footnote_symbol,
    b.bill_num          AS bill_number,
    b.title             AS bill_name,
    b.first_action_date AS date_introduced,
    a.author            AS bill_author,
    -- Dyanmically generate leginfo link by adding session + bill num to URL
    -- TODO: get this from OpenStates directly...
    CONCAT(
            'https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=',
            REPLACE(session, '-', ''), -- Convert YYYY-YYYY to YYYYYYYY
            '0',
            REPLACE(bill_num, ' ', '') -- Remove spaces from bill number
        ) AS leginfo_link
FROM snapshot.hearing_bills hb
LEFT JOIN snapshot.bill b ON b.openstates_bill_id = hb.openstates_bill_id
LEFT JOIN bill_authors a ON a.openstates_bill_id = hb.openstates_bill_id

WITH DATA;

CREATE UNIQUE INDEX idx_hearing_bills_pk ON app.hearing_bills_mv (hearing_id, openstates_bill_id);
CREATE INDEX idx_hearing_bills_hearing ON app.hearing_bills_mv (hearing_id);
CREATE INDEX idx_hearing_bills_bill ON app.hearing_bills_mv (openstates_bill_id);

REFRESH MATERIALIZED VIEW app.hearing_bills_mv;
COMMIT;
-- =============================================================================
-- -- ROLLBACK
-- BEGIN;
-- DROP MATERIALIZED VIEW IF EXISTS app.hearing_bills_mv;
-- CREATE MATERIALIZED VIEW app.hearing_bills_mv AS
-- SELECT
--     hb.hearing_id,
--     hb.openstates_bill_id,
--     hb.file_order,
--     hb.footnote,
--     hb.footnote_symbol,
--     bm.bill_number,
--     bm.bill_name,
--     bm.status,
--     bm.date_introduced,
--     bm.author         AS bill_author,
--     bm.leginfo_link
-- FROM snapshot.hearing_bills hb
-- LEFT JOIN app.bills_mv bm ON bm.openstates_bill_id = hb.openstates_bill_id
-- WITH DATA;

-- CREATE UNIQUE INDEX idx_hearing_bills_pk ON app.hearing_bills_mv (hearing_id, openstates_bill_id);
-- CREATE INDEX idx_hearing_bills_hearing ON app.hearing_bills_mv (hearing_id);
-- CREATE INDEX idx_hearing_bills_bill ON app.hearing_bills_mv (openstates_bill_id);

-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.hearing_bills_mv;
-- COMMIT;
-- =============================================================================