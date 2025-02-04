-- Title: process_bill_history_view2.sql

-- Function that pulls the ca_dev.bill_history tables, merges leg_session from the ca_dev.bill table,
-- and creates a new, clean bill history table as a VIEW. Also filters data by leg session.
-- Output: 
----- schema: public
----- view name: final_processed_bill_history_[legsession]

DROP VIEW IF EXISTS public.bill_history_20252026;
CREATE OR REPLACE VIEW public.bill_history_20252026 AS

-- Get cols from bill history table
WITH temp_history AS (
    SELECT * 
    FROM ca_dev.bill_history
),

-- Get cols from bills table
temp_bills AS (
    SELECT 
		bill_id,
		bill_number,
        leg_session
    FROM ca_dev.bill
),
    
-- Merge data
combined_table AS(
	SELECT
		b.bill_id,
		b.bill_number,
		LEFT(b.leg_session, 4) || '-' || RIGHT(b.leg_session, 4) AS leg_session, -- Format leg_session to have a hyphen (YYYY-YYYY)
		h.event_date,
		h.event_text,
		h.history_order
	FROM temp_bills b
	LEFT JOIN temp_history h ON b.bill_id = h.bill_id
	WHERE LEFT b.leg_session = '2025-2026'  -- Filter by leg session
),
	
    -- Partition the history data based on bill_id and bill_number
partition_history AS (
    SELECT *, 
        FIRST_VALUE(history_order) OVER (PARTITION BY bill_id, bill_number ORDER BY history_order ASC) AS first_history_order
    FROM combined_table
),

filtered_history AS (
    -- Filter data by event_date (e.g., after '2024-12-02', when 2025-2026 session started)
    SELECT *
    FROM partition_history
    WHERE event_date >= '2024-12-02'

)
-- Get final view
SELECT * 
FROM filtered_history
ORDER BY bill_id, history_order
