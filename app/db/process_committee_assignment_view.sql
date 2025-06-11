-- Title: process_committee_assignment_view.sql

-- Processes committee assignment (i.e. committee memberships) for display

-- Inputs: 
----- ca_dev.committee_assignment
----- ca_dev.committee
----- ca_dev.legislator

-- Output: 
----- schema: public
----- view name: processed_committed_assignemnt_[leg_session]

DROP VIEW IF EXISTS processed_committee_assignment_2025_2026;
CREATE OR REPLACE VIEW processed_committee_assignment_2025_2026 AS

-- Get columns from bill action table
WITH temp_assign AS (
    SELECT 
		committee_assignment_id,
        legislator_id,
        committee_id,
        assignment_type,
		LEFT(session, 4) || '-' || RIGHT(session, 4) AS leg_session -- Format leg_session to have a hyphen (YYYY-YYYY)
    FROM ca_dev.committee_assignment
	WHERE LEFT(session, 4) || '-' || RIGHT(session, 4) = '2025-2026' 
),

-- Get columns from committee table
temp_committee AS (
    SELECT
        committee_id,
        chamber_id,
        name AS committee_name
    FROM ca_dev.committee
),

temp_legislator AS (
    SELECT
        legislator_id,
        chamber_id,
        name AS legislator_name,
        district,
        party
    FROM ca_dev.legislator
),

-- Merge committee name data onto assignments
committee_name_assign AS (
    SELECT
        cm.committee_assignment_id,
        cm.legislator_id,
        c.committee_name,
        c.committee_id,
        c.chamber_id,
        cm.assignment_type,
        cm.leg_session
    FROM temp_assign cm
    LEFT JOIN temp_committee c ON cm.committee_id = c.committee_id
),

-- Merge legislator name data onto assignments
named_assign AS (
    SELECT
        cna.committee_assignment_id,
        cna.committee_name,
        cna.committee_id,
        cna.chamber_id,
        cna.assignment_type,
        cp.legislator_name,
        cp.district,
        cp.party,
        cna.leg_session
    FROM committee_name_assign cna
    LEFT JOIN temp_legislator cp ON cp.legislator_id = cna.legislator_id
)

-- Get final view
SELECT * 
FROM named_assign
ORDER BY chamber_id, committee_name;

