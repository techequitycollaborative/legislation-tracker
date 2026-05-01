-- Title: process_hearings_view.sql
-- Creates app.hearings view (not a materialized view)
-- This is a stopgap until we can add the hearings MVs refresh to the daily update 
-- One row per hearing (no bill data)
-- Sources: snapshot.hearings, snapshot.hearing_deadlines

DROP VIEW IF EXISTS app.hearings;
CREATE VIEW app.hearings AS
SELECT
    h.hearing_id,
    h.date           AS hearing_date,
    h.name           AS hearing_name,
    h.time_verbatim  AS hearing_time_verbatim,
    h.time_normalized AS hearing_time,
    h.is_allday,
    h.location       AS hearing_location,
    h.room           AS hearing_room,
    h.chamber_id,
    h.committee_id,
    h.canceled_at,
    h.created_at,
    h.updated_at
FROM snapshot.hearings h;


