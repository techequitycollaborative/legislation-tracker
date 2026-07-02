-- Title: process_hearing_bills_view.sql
-- Creates app.hearing_bills view
-- One row per bill per hearing
-- Sources: snapshot.hearing_bills, app.bills_mv

DROP VIEW IF EXISTS app.hearing_bills;
CREATE VIEW app.hearing_bills AS
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
LEFT JOIN app.bills_mv bm ON bm.openstates_bill_id = hb.openstates_bill_id;