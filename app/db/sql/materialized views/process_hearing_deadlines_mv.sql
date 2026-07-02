-- Title: process_hearing_deadlines_mv.sql
-- Creates app.hearing_deadlines_mv materialized view
-- One row per deadline per hearing
-- Sources: snapshot.hearing_deadlines, snapshot.hearings

DROP MATERIALIZED VIEW IF EXISTS app.hearing_deadlines_mv;
CREATE MATERIALIZED VIEW app.hearing_deadlines_mv AS
SELECT
    hd.id,
    hd.hearing_id,
    hd.deadline_date,
    hd.deadline_type,
    h.date           AS hearing_date,
    h.name           AS hearing_name,
    h.chamber_id,
    h.committee_id
FROM snapshot.hearing_deadlines hd
JOIN snapshot.hearings h ON h.hearing_id = hd.hearing_id
WITH DATA;

CREATE UNIQUE INDEX idx_hearing_deadlines_pk ON app.hearing_deadlines_mv (id);
CREATE INDEX idx_hearing_deadlines_hearing ON app.hearing_deadlines_mv (hearing_id);
CREATE INDEX idx_hearing_deadlines_date ON app.hearing_deadlines_mv (deadline_date);

-- REFRESH MATERIALIZED VIEW CONCURRENTLY app.hearing_deadlines_mv;