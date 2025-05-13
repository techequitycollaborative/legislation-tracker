-- dashboard_tables.sql
-- Create dashboard tables

-- Table: user_bill_dashboard -- this table stores bills that users add to their individual dashboards
CREATE TABLE IF NOT EXISTS user_bill_dashboard (
    user_bill_dashboard_id SERIAL PRIMARY KEY,
    user_email TEXT,
    added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bill_number TEXT,
    openstates_bill_id TEXT,
    org_id INT
);


-- Table: org_bill_dashboard -- this table stores bills that users add to their ORG dashboards
CREATE TABLE IF NOT EXISTS org_bill_dashboard (
    org_bill_dashboard_id SERIAL PRIMARY KEY,
    user_email TEXT,
    added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bill_number TEXT,
    openstates_bill_id TEXT,
    org_id INT
);
