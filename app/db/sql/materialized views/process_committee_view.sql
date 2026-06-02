-- Title: process_committee_view.sql

-- Pulls committee data from PostgreSQL and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot and App schema s
-- Ouputs final, clean committee table for the legislation tracker as a SQL materialized view including next upcoming hearing, 
-- links, chairs, vice chairs, and membership lists

-- Inputs: 
----- snapshot.committee: for most committee info
----- snapshot.hearings: for all upcoming bill events
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
upcoming_hearings AS (
    SELECT DISTINCT ON (c.committee_id)
        c.committee_id,
        h.chamber_id, 
        h.date, 
        h.name
    FROM snapshot.hearings h
    JOIN temp_committee c ON c.committee_id = h.committee_id
	-- Committees can have multiple hearing dates, so only grab the one that occurs after today's date
    WHERE h.date >= CURRENT_DATE
    ORDER BY c.committee_id, h.date ASC
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
    uh.date::date AS committee_event,
    fm.committee_chair,
    fm.committee_vice_chair,
    fm.committee_members,
    fm.member_count,
    fm.total_members
FROM temp_committee c
LEFT JOIN upcoming_hearings uh ON c.committee_id = uh.committee_id
LEFT JOIN full_membership fm ON c.committee_id = fm.committee_id;

-- Create unique index
CREATE UNIQUE INDEX ON app.committees_mv (committee_id);
-- Refresh when needed (for manual refreshes)
--REFRESH MATERIALIZED VIEW CONCURRENTLY app.committees_mv;
