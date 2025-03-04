-- Title: process_bills_view.sql

-- Pulls bill data from various tables to create final, clean bills table for the Streamlit app, 
-- as a SQL view (not as a table) including latest status, date introduced, and properly formatted bill 
-- history columns.

-- Inputs: 
----- ca_dev.bill: for most bill info
----- public.bill_history_20252026: for filtered and processed bill history events
----- ca_dev.bill_schedule: for upcoming bill events for the current legislative session (senate & assembly)
----- snapshot.bill: for date_introduced (i.e. first_action_date)

-- Output: 
----- schema: public
----- view name: processed_bills_20252026

DROP VIEW IF EXISTS processed_bills_20252026;
CREATE OR REPLACE VIEW processed_bills_20252026 AS

-- Copy data from ca_dev.bill and clean up
WITH temp_bills AS (
    SELECT 
		openstates_bill_id,
        bill_id,
        bill_number,
        bill_name,
		author,   
	    coauthors, 
		leginfo_link,
		full_text,
		LEFT(leg_session, 4) || '-' || RIGHT(leg_session, 4) AS leg_session, -- Format leg_session to have a hyphen (YYYY-YYYY)
        CASE 
            WHEN origin_chamber_id = 1 THEN 'Assembly'
            ELSE 'Senate'
        END AS chamber
    FROM ca_dev.bill
	WHERE LEFT(leg_session, 4) || '-' || RIGHT(leg_session, 4) = '2025-2026' 
),

-- Get the latest status for each bill from public.bill_history_20252026
latest_status AS (
    SELECT DISTINCT ON (bill_id) 
        bill_id, 
        event_text AS status
    FROM public.bill_history_20252026
    ORDER BY bill_id, event_date DESC
),

-- Aggregate full bill history
full_history AS (
    SELECT 
        bill_id,
        STRING_AGG(event_date || ' >> ' || event_text, ', ' ORDER BY event_date) AS bill_history
    FROM public.bill_history_20252026
    GROUP BY bill_id
)

-- Combine all processed data into a single view
SELECT 
	b.bill_id,
    b.bill_number,
	b.bill_name,
	s.status,
	sp.first_action_date::date AS date_introduced, -- Pull first_action_date (i.e. date_introduced) directly from snapshot.bill table
    b.leg_session,
    b.author,   
    b.coauthors, 
    b.chamber,
	b.leginfo_link,
	b.full_text,
    h.bill_history,
	bs.event_date::date AS bill_event,
    bs.event_text
FROM temp_bills b
LEFT JOIN latest_status s ON b.bill_id = s.bill_id
LEFT JOIN snapshot.bill sp ON b.openstates_bill_id = sp.openstates_bill_id -- Add first_action_date from snapshot bill table
LEFT JOIN full_history h ON b.bill_id = h.bill_id
LEFT JOIN ca_dev.bill_schedule bs ON b.bill_id = bs.bill_id; -- Add bill events from bill schedule table