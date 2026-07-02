-- Title: process_committee_assignment_view.sql
-- Processes committee assignment (i.e. committee memberships) for display

-- Inputs: 
----- snapshot.committee_assignment
----- snapshot.committee

-- Output: 
----- schema: app
----- materialized view name: app.committee_assignments_mv

DROP MATERIALIZED VIEW IF EXISTS app.committee_assignments_mv;

CREATE MATERIALIZED VIEW app.committee_assignments_mv AS

-- Get columns from committee assignment table
WITH temp_assign AS (
    SELECT 
        committee_assignment_id,
        committee_id,
        legislator_name,
        assignment_type,
        LEFT(session, 4) || '-' || RIGHT(session, 4) AS leg_session -- Format leg_session to have a hyphen (YYYY-YYYY)
    FROM snapshot.committee_assignment
),

-- Get columns from committee table
temp_committee AS (
    SELECT
        committee_id,
        chamber_id,
        name AS committee_name
    FROM snapshot.committee
),

-- Merge committee name data onto assignments
committee_name_assign AS (
    SELECT
        cm.committee_assignment_id,
        c.committee_name,
        c.committee_id,
        c.chamber_id,
        cm.legislator_name,
        cm.assignment_type,
        cm.leg_session
    FROM temp_assign cm
    LEFT JOIN temp_committee c ON cm.committee_id = c.committee_id
)
-- Get final view
SELECT * 
FROM committee_name_assign
ORDER BY chamber_id, committee_name;