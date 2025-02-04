-- Title: process_bills_view.sql

-- Function that pulls from ca_dev.bill table and public.bill_history_20252026 view and creates new, 
-- clean bills table AS A VIEW (not as a table) including latest status, date introduced, and properly formatted bill 
-- history columns.

-- Input: 
----- ca_dev.bill: bill info
----- public.bill_history_20252026: filtered and processed bill history events

-- Output: 
----- schema: public
----- view name: final_processed_bills_view

DROP VIEW IF EXISTS processed_bills_20252026;
CREATE OR REPLACE VIEW processed_bills_20252026 AS

-- Step 1: Copy data from ca_dev.bill and clean up
WITH temp_bills AS (
    SELECT 
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

-- Step 2: Get the latest status for each bill from public.bill_history_20252026
latest_status AS (
    SELECT DISTINCT ON (bill_id) 
        bill_id, 
        event_text AS status
    FROM public.bill_history_20252026
    ORDER BY bill_id, event_date DESC
),

-- Step 3: Get the earliest date introduced for each bill from public.bill_history_20252026
earliest_date AS (
    SELECT DISTINCT ON (bill_id)
        bill_id,
        event_date AS date_introduced
    FROM public.bill_history_20252026
    ORDER BY bill_id, event_date ASC
),

-- Step 4: Aggregate full bill history
full_history AS (
    SELECT 
        bill_id,
        STRING_AGG(event_date || ' >> ' || event_text, ', ' ORDER BY event_date) AS bill_history
    FROM public.bill_history_20252026
    GROUP BY bill_id
)

-- Step 5: Combine all processed data into a single view
SELECT 
    b.bill_number,
	b.bill_name,
	s.status,
    e.date_introduced::date,
    b.leg_session,
    b.author,   
    b.coauthors, 
    b.chamber,
	b.leginfo_link,
	b.full_text,
    h.bill_history
FROM temp_bills b
LEFT JOIN latest_status s ON b.bill_id = s.bill_id
LEFT JOIN earliest_date e ON b.bill_id = e.bill_id
LEFT JOIN full_history h ON b.bill_id = h.bill_id
