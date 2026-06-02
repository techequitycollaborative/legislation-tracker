-- =============================================================================
-- Migration: Refactor mat views to remove dependency on snapshot.bill_schedule,
--            and drop deprecated views entirely
-- Run once against legtracker_2026
-- Rollback: not supported - forward fix only
-- Views affected: app.bills, app.bills_mv, app.committees_mv, bills_2025_2026
-- =============================================================================

BEGIN;

-- =============================================================================
-- Drop relations that are no longer in use
-- =============================================================================
DROP VIEW IF EXISTS bills_2025_2026;
DROP VIEW IF EXISTS app.bills;
DROP VIEW IF EXISTS app.hearing_bills;
DROP TABLE IF EXISTS snapshot.bill_schedule;

-- =============================================================================
-- Dropping app.bills_mv and its dependents (bottom-up)
-- =============================================================================
DROP MATERIALIZED VIEW IF EXISTS app.calendar_mv;
DROP MATERIALIZED VIEW IF EXISTS app.hearing_bills_mv;
DROP VIEW IF EXISTS app.org_bill_dashboard_custom;

-- app.bills_mv
DROP MATERIALIZED VIEW IF EXISTS app.bills_mv;

-- =============================================================================
-- Update app.bills_mv definition to use snapshot.hearing_bills
-- =============================================================================

CREATE MATERIALIZED VIEW app.bills_mv AS

-- Copy data from snapshot.bill and clean up
WITH temp_bills AS (
    SELECT 
		openstates_bill_id,
        -- bill_id; We will use open states id from now on bc we started to get duplicates of our own bill id
		LEFT(session, 4) || '-' || RIGHT(session, 4) AS leg_session, -- Format leg_session to have a hyphen (YYYY-YYYY)
		chamber,
		bill_num AS bill_number,
        title AS bill_name,
		first_action_date::date AS date_introduced,
		last_action_date::date AS last_updated_on, 
		abstract AS bill_text,
		-- Dyanmically generate leginfo link by adding session + bill num to URL. URL is not a variable we can pull from OpenStates
		CONCAT(
            'https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=',
            REPLACE(session, '-', ''), -- Convert YYYY-YYYY to YYYYYYYY
            '0',
            REPLACE(bill_num, ' ', '') -- Remove spaces from bill number
        ) AS leginfo_link
    FROM snapshot.bill
	WHERE LEFT(session, 4) || '-' || RIGHT(session, 4) = '2025-2026'
        AND bill.bill_num NOT LIKE 'ACR%'
        AND bill.bill_num NOT LIKE 'HR%'
        AND bill.bill_num NOT LIKE 'SCR%'
        AND bill.bill_num NOT LIKE 'SR%'
        AND bill.bill_num NOT LIKE 'SJR%' 
        AND bill.bill_num NOT LIKE 'AJR%' 
		AND (
            last_action_date >= '2025-12-01' -- Get bills updated on or after 2025-12-01
			-- OR get bills with 'inactive file' in their latest status (our way of grabbing 2-year bills)
            OR openstates_bill_id IN (
                SELECT DISTINCT openstates_bill_id 
                FROM app.bill_history 
                WHERE LOWER(description) LIKE '%inactive file%'
            )
			OR bill_num = 'AB 412'
			OR bill_num = 'SB 435'
        )
		
),

-- Get the latest status for each bill from app.bill_history
latest_status AS (
    SELECT DISTINCT ON (openstates_bill_id) 
        openstates_bill_id, 
        description AS status
    FROM app.bill_history
	-- Make sure action_order is treated as in integer for order to be handled correctly
    ORDER BY openstates_bill_id, action_order::integer DESC
),

-- Aggregate full bill history
full_history AS (
    SELECT 
        openstates_bill_id,
        STRING_AGG(action_date || ' >> ' || description, ', ' ORDER BY action_date) AS bill_history
    FROM app.bill_history
    GROUP BY openstates_bill_id
),

-- Process bill sponsors to get primary author and coauthors
bill_authors AS (
    SELECT 
        openstates_bill_id,
        MAX(CASE WHEN primary_author = 'True' THEN full_name END) AS author,
        STRING_AGG(CASE WHEN primary_author = 'False' THEN full_name END, ', ') AS coauthors
    FROM snapshot.bill_sponsor
    GROUP BY openstates_bill_id
),

-- Deduplicate hearing_bills: if multiple rows per bill exist, keep the soonest 
-- If no row exists, both hearing_date and hearing_name will be NULL
bill_hearings AS (
    SELECT DISTINCT ON (hb.openstates_bill_id)
        hb.id,
        hb.hearing_id,
        hb.openstates_bill_id,
        hb.file_order,
        h.date AS hearing_date,
        h.name AS hearing_name
    FROM snapshot.hearing_bills hb
    JOIN snapshot.hearings h ON hb.hearing_id = h.hearing_id
    WHERE h.date >= CURRENT_DATE
    ORDER BY hb.openstates_bill_id, h.date ASC
),

-- Get bill topics
bill_topics AS (
    SELECT
        openstates_bill_id,
        STRING_AGG(bt.topic_phrase, '; ' ORDER BY bt.topic_phrase ASC) AS assigned_topics
    FROM (
        SELECT DISTINCT
        openstates_bill_id,
        topic_phrase
        FROM snapshot.bill_topics
    ) as bt
    GROUP BY openstates_bill_id
)

-- Combine all processed data into a single view
SELECT 
	b.openstates_bill_id,
    b.bill_number,
	b.bill_name,
	s.status,
	b.date_introduced::date,
    b.leg_session,
    a.author,
    a.coauthors, 
    b.chamber,
	b.leginfo_link,
	b.bill_text,
    h.bill_history,
	bh.hearing_date::date AS bill_event,
    bh.hearing_name AS event_text,
    t.assigned_topics,
    b.last_updated_on::date
FROM temp_bills b
LEFT JOIN latest_status s ON b.openstates_bill_id = s.openstates_bill_id
LEFT JOIN full_history h ON b.openstates_bill_id = h.openstates_bill_id
LEFT JOIN bill_authors a ON b.openstates_bill_id = a.openstates_bill_id
LEFT JOIN bill_hearings bh ON b.openstates_bill_id = bh.openstates_bill_id -- Add bill events from bill schedule table (without dupes)
LEFT JOIN bill_topics t ON b.openstates_bill_id = t.openstates_bill_id;

-- UNIQUE index to use CONCURRENTLY (refresh view without interruption)
CREATE UNIQUE INDEX idx_bills_mv_pk ON app.bills_mv(openstates_bill_id);

-- =============================================================================
-- Recreate app.calendar_mv (definitions unchanged, forced recreate)
-- =============================================================================
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
	hb.file_order,
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

-- =============================================================================
-- Recreate app.hearing_bills_mv (definitions unchanged, forced recreate)
-- =============================================================================
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

-- =============================================================================
-- Recreate app.org_bill_dashboard_custom (definitions unchanged, forced recreate)
-- =============================================================================
CREATE OR REPLACE VIEW app.org_bill_dashboard_custom AS
SELECT 
    b.openstates_bill_id,
    b.bill_number,
    b.bill_name,
    b.status,
    b.date_introduced,
    b.leg_session,
    b.author,
    b.coauthors, 
    b.chamber,
    b.leginfo_link,
    b.bill_text,
    b.bill_history,
    b.bill_event,
    b.event_text,
    b.assigned_topics,
    b.last_updated_on,
    -- Grab org id from org_bill_dashboard
    obd.org_id,
    -- Custom details from bill_custom_details; just org_position and assigned_to for now
    bcd.org_position,
    --bcd.priority_tier,
    --bcd.community_sponsor,
    --bcd.coalition,
    bcd.assigned_to,
    --bcd.action_taken
	bcd.last_updated_on AS changed_on
FROM app.bills_mv b
INNER JOIN app.org_bill_dashboard obd
    ON obd.openstates_bill_id = b.openstates_bill_id
LEFT JOIN app.bill_custom_details bcd
    ON bcd.openstates_bill_id = b.openstates_bill_id
    AND bcd.last_updated_org_id = obd.org_id;

-- =============================================================================
-- Update app.committees_mv definition 
-- =============================================================================

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

COMMIT;
