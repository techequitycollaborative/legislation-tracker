-- Title: process_legislators_from_snapshot.sql

-- Pulls people data from OpenStates API and processes for display in Streamlit app.
-- Sources data from various tables in the Snapshot schema 
-- Ouputs final, clean legislators table for the legislation tracker as a SQL view (not as a table) including Capitol Office,
-- district office(s), corresponding phone numbers, alternate names, and external sources

-- Inputs: 
----- snapshot.people: for core people info
----- snapshot.people_roles: for chamber designation, district number
----- snapshot.people_names: for alternate names
----- snapshot.people_offices: any office address and phone number
----- snapshot.people_sources: for (primary) source URLs


-- Output: 
----- schema: app
----- view name: legislators

DROP VIEW IF EXISTS app.legislators;
CREATE OR REPLACE VIEW app.legislators AS

-- Copy data from snapshot.people and clean up
WITH temp_people AS (
    SELECT 
		openstates_people_id,
        name, -- apply transform name at snapshot level
        party,
        updated_at
    FROM snapshot.people
),

-- Get the role for each person from snapshot.people_roles
temp_roles AS (
    SELECT DISTINCT ON (openstates_people_id) 
        openstates_people_id, 
        district,
        CASE WHEN org_classification = 'lower' THEN 'Assembly' ELSE 'Senate' END AS chamber
    FROM snapshot.people_roles
),

-- Get all alternate names for each person from snapshot.people_names
temp_names AS (
    SELECT
        openstates_people_id, 
        STRING_AGG(alt_name, '; ' ORDER BY alt_name) other_names
    FROM snapshot.people_names
    GROUP BY openstates_people_id
),

-- Get all external sources for each person from snapshot.people_sources
temp_sources AS (
    SELECT
        openstates_people_id, 
        STRING_AGG(source_url, '\n') AS ext_sources
    FROM snapshot.people_sources
    GROUP BY openstates_people_id
),

-- Select capitol offices (only 1 per legislator) and district offices (more than 1 per legislator)
temp_offices AS (
    SELECT openstates_people_id,
    STRING_AGG(CASE WHEN classification = 'capitol' THEN name ELSE SPLIT_PART(address, ', ', -2) END || '@@' || 'Phone: ' || phone || '@@' || address, '\n') office_details
    FROM snapshot.people_offices 
    GROUP BY openstates_people_id
),

temp_contacts AS (
    SELECT
        openstates_people_id,
        STRING_AGG(people_contact_id || '@@' || issue_area || '@@' || staffer_type || '@@' || staffer_contact || '@@' || generated_email, '\n') AS issue_contacts
        FROM snapshot.people_contacts
        GROUP BY openstates_people_id
)
-- Combine all processed data into a single view
SELECT 
    p.openstates_people_id,
    p.updated_at::date AS last_updated_on,
    p.name,
    p.party,
    r.chamber,
    r.district,
    n.other_names,
    s.ext_sources,
    o.office_details,
    c.issue_contacts
FROM temp_people p
LEFT JOIN temp_roles r ON p.openstates_people_id = r.openstates_people_id
LEFT JOIN temp_names n ON p.openstates_people_id = n.openstates_people_id
LEFT JOIN temp_sources s ON p.openstates_people_id = s.openstates_people_id
LEFT JOIN temp_offices o ON p.openstates_people_id = o.openstates_people_id
LEFT JOIN temp_contacts c ON p.openstates_people_id = c.openstates_people_id; 