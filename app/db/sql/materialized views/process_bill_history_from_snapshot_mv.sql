-- Title: process_bill_history_from_snapshot.sql

-- Processes bill actions (i.e. bill history) directly from OpenStates.
-- Creates a MATERIALIZED VIEW

-- Inputs: 
----- snapshot.bill
----- snapshot.bill_action

-- Output: 
----- schema: app
----- materialized view name: bill_history_mv

DROP MATERIALIZED VIEW IF EXISTS app.bill_history_mv;
CREATE MATERIALIZED VIEW app.bill_history_mv AS

-- Get columns from bill action table
WITH temp_action AS (
    SELECT * FROM snapshot.bill_action
),

-- Get columns from bills table
temp_bills AS (
    SELECT
        openstates_bill_id,
        bill_num,
        session
    FROM snapshot.bill
    WHERE LEFT(session, 4) = '2025'  -- Filter before transformation
),

-- Merge data
combined_table AS (
    SELECT
        b.openstates_bill_id,
        b.bill_num,
        LEFT(b.session, 4) || '-' || RIGHT(b.session, 4) AS leg_session, -- Format leg_session to YYYY-YYYY
        a.action_date,
        a.description,
        a.action_order
    FROM temp_bills b
    LEFT JOIN temp_action a ON b.openstates_bill_id = a.openstates_bill_id
),

-- Partition the bill action data based on bill_id and bill_number
partition_action AS (
    SELECT *, 
        FIRST_VALUE(action_order) OVER (PARTITION BY openstates_bill_id, bill_num ORDER BY action_order ASC) AS first_action_order
    FROM combined_table
),

filtered_action AS (
    -- Filter data by action_date (e.g., after '2024-12-02', when 2025-2026 session started)
    SELECT *
    FROM partition_action
    WHERE action_date >= '2024-12-02'
)

-- Get final view and a unique row index
SELECT 
    ROW_NUMBER() OVER (ORDER BY openstates_bill_id, action_order, action_date) AS row_id,
    *
FROM filtered_action
ORDER BY openstates_bill_id, action_order;

-- Then create the unique index on row_id:
CREATE UNIQUE INDEX idx_bill_history_mv_pk ON app.bill_history_mv(row_id);