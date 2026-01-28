-- Title: process_committee_view.sql

-- Pulls committee data from PostgreSQL and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot and App schema s
-- Ouputs final, clean committee table for the legislation tracker as a SQL materialized view including next upcoming hearing, 
-- links, chairs, vice chairs, and membership lists

-- Inputs: 
----- snapshot.committee: for most committee info
----- snapshot.bill_schedule: for all upcoming bill events
----- app.committee_assignment_mv: for filtered/processed committee assignment information

-- Output: 
----- schema: app
----- view name: app.committees_mv

DROP MATERIALIZED VIEW IF EXISTS app.committees_mv;
CREATE MATERIALIZED VIEW app.committees_mv AS

-- Copy data from snapshot.committee
WITH temp_committee AS (
    SELECT 
		committee_id,
        chamber_id,
        name AS committee_name,
        webpage_link
    FROM snapshot.committee
),

-- Get all distinct upcoming committee hearings by partial string match of event text to committee name
upcoming_schedule AS (
    SELECT DISTINCT 
        bs.chamber_id, 
        bs.event_date, 
        bs.event_text,
        c.committee_id
    FROM snapshot.bill_schedule bs
    JOIN temp_committee c 
        ON (c.committee_name LIKE CONCAT('%', event_text, '%') AND c.chamber_id = bs.chamber_id)
),

-- Aggregate full committee membership
full_membership AS (
    SELECT 
        committee_id,
        MAX(CASE WHEN assignment_type = 'Chair' THEN legislator_name ELSE NULL END) AS committee_chair,
        MAX(CASE WHEN assignment_type = 'Vice Chair' THEN legislator_name ELSE NULL END) AS committee_vice_chair,
        STRING_AGG(CASE WHEN assignment_type = 'Member' THEN legislator_name END, '; ') AS committee_members,
        COUNT(CASE WHEN assignment_type = 'Member' THEN 1 END) AS member_count, -- count only normal members
        COUNT(CASE WHEN assignment_type IN ('Member', 'Chair', 'Vice Chair') THEN 1 END) AS total_members -- count all members
    FROM app.committee_assignments_mv
    GROUP BY committee_id
)

-- Combine all processed data into a single view
SELECT
    c.committee_id,
    c.chamber_id,
    c.committee_name,
    c.webpage_link,
    us.event_date::date AS committee_event,
    fm.committee_chair,
    fm.committee_vice_chair,
    fm.committee_members,
    fm.member_count,
    fm.total_members
FROM temp_committee c
LEFT JOIN upcoming_schedule us ON c.committee_id = us.committee_id
LEFT JOIN full_membership fm ON c.committee_id = fm.committee_id;
