-- Title: process_hearing_deadlines_view.sql
-- Creates app.hearing_deadlines view
-- One row per deadline per hearing
-- Sources: snapshot.hearing_deadlines, snapshot.hearings

DROP VIEW IF EXISTS app.hearing_deadlines;
CREATE VIEW app.hearing_deadlines AS
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
JOIN snapshot.hearings h ON h.hearing_id = hd.hearing_id;