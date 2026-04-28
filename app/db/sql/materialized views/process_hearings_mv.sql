-- Title: process_hearings_mv.sql
-- Creates app.hearings materialized view
-- One row per hearing (no bill data)
-- Sources: snapshot.hearings, snapshot.hearing_deadlines

DROP MATERIALIZED VIEW IF EXISTS app.hearings_mv;
CREATE MATERIALIZED VIEW app.hearings_mv AS
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
FROM snapshot.hearings h
WITH DATA;

CREATE UNIQUE INDEX idx_hearings_pk ON app.hearings_mv (hearing_id);
CREATE INDEX idx_hearings_date ON app.hearings_mv (hearing_date);
CREATE INDEX idx_hearings_chamber ON app.hearings_mv (chamber_id);

-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.hearings_mv;