-- Title: process_bills_from_snapshot.sql

-- Pulls bill data from OpenStates API and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot schema 
-- Ouputs final, clean bills table for the legislation tracker as a SQL view (not as a table) including latest status, 
-- date introduced, and properly formatted bill history columns.

-- Inputs: 
----- snapshot.bill: for most bill info
----- public.processed_bill_action_2025_2026: for filtered/processed bill history/bill action
----- snapshot.bill_sponsor: for author, coauthors
----- ca_dev.bill_schedule: for upcoming bill events for the current legislative session (senate & assembly)

-- Output: 
----- schema: public
----- view name: processed_bills_from_snapshot_{leg_session}

DROP VIEW IF EXISTS processed_bills_from_snapshot_2025_2026;
CREATE OR REPLACE VIEW processed_bills_from_snapshot_2025_2026 AS

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
),

-- Get the latest status for each bill from public.processed_bill_action_2025_2026
latest_status AS (
    SELECT DISTINCT ON (openstates_bill_id) 
        openstates_bill_id, 
        description AS status
    FROM public.processed_bill_action_2025_2026
    ORDER BY openstates_bill_id, action_date DESC
),

-- Aggregate full bill history
full_history AS (
    SELECT 
        openstates_bill_id,
        STRING_AGG(action_date || ' >> ' || description, ', ' ORDER BY action_date) AS bill_history
    FROM public.processed_bill_action_2025_2026
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
)

-- Combine all processed data into a single view
SELECT 
	b.openstates_bill_id,
    b.bill_number,
	b.bill_name,
	s.status,
	b.date_introduced,
    b.leg_session,
    a.author,
    a.coauthors, 
    b.chamber,
	b.leginfo_link,
	b.bill_text,
    h.bill_history,
	bs.event_date::date AS bill_event,
    bs.event_text
FROM temp_bills b
LEFT JOIN latest_status s ON b.openstates_bill_id = s.openstates_bill_id
LEFT JOIN full_history h ON b.openstates_bill_id = h.openstates_bill_id
LEFT JOIN bill_authors a ON b.openstates_bill_id = a.openstates_bill_id
LEFT JOIN ca_dev.bill_schedule bs ON b.openstates_bill_id = bs.openstates_bill_id; -- Add bill events from bill schedule table