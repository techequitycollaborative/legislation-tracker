--committee_assignment.sql
-- Creates snapshot.committee_assignment table

-- Create the committee_assignment table
DROP TABLE IF EXISTS snapshot.committee_assignment;
CREATE TABLE snapshot.committee_assignment (
    committee_assignment_id SERIAL PRIMARY KEY,
    committee_id INTEGER NOT NULL,
    chamber_id INTEGER NOT NULL,
    legislator_name VARCHAR(255) NOT NULL,
    assignment_type VARCHAR(50) NOT NULL,
    session VARCHAR(20) NOT NULL DEFAULT '20252026',
    FOREIGN KEY (committee_id) REFERENCES snapshot.committee(committee_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_committee_assignment_committee_id 
    ON snapshot.committee_assignment(committee_id);
CREATE INDEX IF NOT EXISTS idx_committee_assignment_chamber_id 
    ON snapshot.committee_assignment(chamber_id);
CREATE INDEX IF NOT EXISTS idx_committee_assignment_session 
    ON snapshot.committee_assignment(session);
CREATE INDEX IF NOT EXISTS idx_committee_assignment_legislator 
    ON snapshot.committee_assignment(legislator_name);

-- Insert data from the CSV, joining with snapshot.committee to get committee_id
-- Using a temporary table to load CSV data first
CREATE TEMP TABLE temp_assignments (
    name VARCHAR(255),
    chamber_id INTEGER,
    legislator_name VARCHAR(255),
    assignment VARCHAR(50)
);

-- Load CSV into temp table
-- Run this via terminal:
-- \copy temp_assignments(name, chamber_id, legislator_name, assignment) FROM 'path.csv' WITH CSV HEADER;

-- Insert into final table by joining with snapshot.committee to get committee_id
INSERT INTO snapshot.committee_assignment (
    committee_id,
    chamber_id,
    legislator_name,
    assignment_type,
    session
)
SELECT 
    c.committee_id,
    c.chamber_id,
    ta.legislator_name,
    ta.assignment,
    '20252026' AS session
FROM temp_assignments ta
INNER JOIN snapshot.committee c 
    ON c.name = ta.name 
    AND c.chamber_id = ta.chamber_id
ORDER BY c.committee_id, 
    CASE 
        WHEN ta.assignment = 'Chair' THEN 1
        WHEN ta.assignment = 'Vice Chair' THEN 2
        WHEN ta.assignment = 'Member' THEN 3
    END,
    ta.legislator_name;

-- Drop the temporary table
DROP TABLE IF EXISTS temp_assignments;

-- Verify the insert
SELECT 
    COUNT(*) as total_assignments,
    COUNT(DISTINCT committee_id) as unique_committees,
    COUNT(DISTINCT chamber_id) as unique_chambers,
    COUNT(DISTINCT legislator_name) as unique_legislators
FROM snapshot.committee_assignment
WHERE session = '20252026';