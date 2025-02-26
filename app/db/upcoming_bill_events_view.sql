-- Create upcoming bill events view that includes upcoming committee hearing date and referred committee columns.
---- Schema: Public
---- Inputs: public.bill_history_20252026
---- Outputs: public.upcoming_bill_events_20252026

DROP VIEW IF EXISTS upcoming_bill_events_20252026;

CREATE VIEW upcoming_bill_events_20252026 AS
SELECT 
    bh.bill_id,
    bh.bill_number,
    bh.leg_session,

    -- Extracts the first upcoming committee hearing date per bill_id
    MAX(
        CASE 
            WHEN bh.event_text ~ 'May be heard in committee' THEN 
                TO_DATE((regexp_match(bh.event_text, '(\w+ \d{1,2})'))[1] || ' ' || EXTRACT(YEAR FROM CURRENT_DATE), 'Month DD YYYY')
            ELSE NULL
        END
    ) AS upcoming_comm_mtg,

    -- Aggregates unique referred committee names into a comma-separated list
    STRING_AGG(
        DISTINCT (regexp_match(bh.event_text, 'Com\. on ([^\.]+)'))[1],
        ', '
    ) FILTER (WHERE bh.event_text ~ 'Com\. on') AS referred_committee

FROM bill_history_20252026 bh
GROUP BY bh.bill_id, bh.bill_number, bh.leg_session;
