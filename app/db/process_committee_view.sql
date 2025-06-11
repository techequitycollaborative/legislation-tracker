-- Title: process_committee_view.sql

-- Pulls bill data from OpenStates API and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot schema 
-- Ouputs final, clean bills table for the legislation tracker as a SQL view (not as a table) including latest status, 
-- date introduced, and properly formatted bill history columns.

-- Inputs: 
----- ca_dev.committee: for most committee info
----- public.processed_committee_assignment_2025_2026: for filtered/processed committee assignment information
----- snapshot.bill_sponsor: for author, coauthors
----- ca_dev.bill_schedule_new: for upcoming bill events for the current legislative session (senate & assembly)

-- Output: 
----- schema: public
----- view name: processed_bills_from_snapshot_{leg_session}

DROP VIEW IF EXISTS processed_committee_2025_2026;
CREATE OR REPLACE VIEW processed_committee_2025_2026 AS

-- Copy data from ca_dev.committee
WITH temp_committee AS (
    SELECT 
		committee_id,
        chamber_id,
        name AS committee_name,
        webpage_link
    FROM ca_dev.committee
),

-- Get all distinct upcoming committee hearings by partial string match of event text to committee name
upcoming_schedule AS (
    SELECT DISTINCT 
        bs.chamber_id, 
        bs.event_date, 
        bs.event_text,
        c.committee_id
    FROM ca_dev.bill_schedule bs
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
    FROM public.processed_committee_assignment_2025_2026
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
