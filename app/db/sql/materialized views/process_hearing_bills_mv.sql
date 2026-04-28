-- Title: process_hearing_bills_mv.sql
-- Creates app.hearing_bills_mv materialized view
-- One row per bill per hearing
-- Sources: snapshot.hearing_bills, app.bills_mv

DROP MATERIALIZED VIEW IF EXISTS app.hearing_bills_mv;
CREATE MATERIALIZED VIEW app.hearing_bills_mv AS
SELECT
    hb.hearing_id,
    hb.openstates_bill_id,
    hb.file_order,
    hb.footnote,
    hb.footnote_symbol,
    bm.bill_number,
    bm.bill_name,
    bm.status,
    bm.date_introduced,
    bm.author         AS bill_author,
    bm.leginfo_link
FROM snapshot.hearing_bills hb
LEFT JOIN app.bills_mv bm ON bm.openstates_bill_id = hb.openstates_bill_id
WITH DATA;

CREATE UNIQUE INDEX idx_hearing_bills_pk ON app.hearing_bills_mv (hearing_id, openstates_bill_id);
CREATE INDEX idx_hearing_bills_hearing ON app.hearing_bills_mv (hearing_id);
CREATE INDEX idx_hearing_bills_bill ON app.hearing_bills_mv (openstates_bill_id);

-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.hearing_bills_mv;