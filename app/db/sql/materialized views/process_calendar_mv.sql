-- Title: process_calendar_mv.sql

-- Pulls hearing data and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot schema 
-- Ouputs final, clean calendar mat view for the legislation tracker
-- Creates a MATERIALIZED VIEW

-- Inputs: 
----- snapshot.hearing_bills: for bills scheduled to hearings
----- snapshot.hearings: for hearing details
----- snapshot.hearing_deadlines: for event-level deadlines

-- Output: 
----- schema: app
----- materialized view name: calendar_mv
CREATE MATERIALIZED VIEW app.calendar_mv AS
SELECT
    hb.openstates_bill_id,
    bm.bill_number,
    bm.bill_name,
    bm.status,
    bm.date_introduced,
    h.hearing_id,
    h.date AS hearing_date,
    h.name AS hearing_name,
    h.time_verbatim AS hearing_time_verbatim,
    h.time_normalized AS hearing_time,
    h.is_allday,
    h.location AS hearing_location,
    h.room AS hearing_room,
    h.chamber_id,
    h.committee_id,
    hd.deadline_date,
    hd.deadline_type,
    h.created_at,
    h.updated_at
FROM snapshot.hearing_bills hb
JOIN snapshot.hearings h ON hb.hearing_id = h.hearing_id
LEFT JOIN snapshot.hearing_deadlines hd ON hd.hearing_id = h.hearing_id -- edge case where deadlines haven't been generated yet
LEFT JOIN app.bills_mv bm ON bm.openstates_bill_id = hb.openstates_bill_id
WITH DATA; -- mat view is populated immediately

CREATE INDEX idx_hearing_events_bill_id ON app.calendar_mv (openstates_bill_id);
CREATE INDEX idx_hearing_events_org ON app.calendar_mv (openstates_bill_id) INCLUDE (hearing_date, deadline_date);
CREATE UNIQUE INDEX idx_calendar_mv_pk ON app.calendar_mv (hearing_id, openstates_bill_id);
