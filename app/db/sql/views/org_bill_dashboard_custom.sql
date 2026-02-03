-- org_bill_dashboard_custom.sql
-- This script creates a sql view that joins bills from an organization's org dashboard with the 
-- custom advocacy details from the org dashboard. 
-- Inputs: bills_mv, org_bill_dashboard, bill_custom_details
-- Output: 
---- schema: app
---- view name: org_bill_dashboard_custom
-- Create a view that joins bills with custom details

DROP VIEW IF EXISTS app.org_bill_dashboard_custom;

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
    bcd.assigned_to
    --bcd.action_taken
FROM app.bills_mv b
INNER JOIN app.org_bill_dashboard obd
    ON obd.openstates_bill_id = b.openstates_bill_id
LEFT JOIN app.bill_custom_details bcd
    ON bcd.openstates_bill_id = b.openstates_bill_id
    AND bcd.last_updated_org_id = obd.org_id;
