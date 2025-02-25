-- Create upcoming bill events view that includes upcoming committee hearing date and referred committee columns.
---- Schema: Public
---- Inputs: ca_dev.bill_history
---- Outputs: public.upcoming_bill_events_20252026

DROP VIEW IF EXISTS upcoming_bill_events_20252026;

CREATE VIEW upcoming_bill_events_20252026 AS
SELECT 
    bh.bill_id,
    bh.bill_number,
    bh.leg_session,
    bh.event_text,

    -- Extracts the upcoming committee hearing date, or 'None' if no match is found
    COALESCE(
        CASE 
            WHEN bh.event_text ~ 'May be heard in committee' THEN 
                TO_DATE((regexp_match(bh.event_text, '(\w+ \d{1,2})'))[1] || ' ' || EXTRACT(YEAR FROM CURRENT_DATE), 'Month DD YYYY')
        END::TEXT, 
        'None'
    ) AS upcoming_comm_mtg,

    -- Extracts only the committee name (text after "Com. on " and before next period ".")
    COALESCE(
        (SELECT (regexp_match(bh.event_text, 'Com\. on ([^\.]+)'))[1]),
        'None'
    ) AS referred_committee

FROM bill_history_20252026 bh;
