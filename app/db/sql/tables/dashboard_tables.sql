-- dashboard_tables.sql
-- Create dashboard tables

-- Table: user_bill_dashboard -- this table stores bills that users add to their individual dashboards
CREATE TABLE IF NOT EXISTS app.user_bill_dashboard (
    user_bill_dashboard_id SERIAL PRIMARY KEY,
    user_email TEXT,
    added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bill_number TEXT,
    openstates_bill_id TEXT,
    org_id INT
);


-- Table: org_bill_dashboard -- this table stores bills that users add to their ORG dashboards
CREATE TABLE IF NOT EXISTS app.org_bill_dashboard (
    org_bill_dashboard_id SERIAL PRIMARY KEY,
    user_email TEXT,
    added_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bill_number TEXT,
    openstates_bill_id TEXT,
    org_id INT
);

-- Table: bill_custom_details -- this table stores custom details for bills (which is rendered on the org dashboard)
CREATE TABLE IF NOT EXISTS app.bill_custom_details (
    bill_custom_details_id SERIAL PRIMARY KEY,
    bill_number TEXT,
    org_position TEXT, 
    priority_tier TEXT,
    community_sponsor TEXT,
    coalition TEXT,
    letter_of_support TEXT,
    openstates_bill_id TEXT,
    assigned_to TEXT,
    action_taken TEXT,
    last_updated_by TEXT,
    last_updated_org_id INT,
    last_updated_org_name TEXT,
    last_updated_on DATE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes on underlying tables for better view performance
CREATE INDEX IF NOT EXISTS idx_org_bill_dashboard_org_id 
    ON app.org_bill_dashboard(org_id);

CREATE INDEX IF NOT EXISTS idx_org_bill_dashboard_bill_id 
    ON app.org_bill_dashboard(openstates_bill_id);

CREATE INDEX IF NOT EXISTS idx_bill_custom_details_bill_id
    ON app.bill_custom_details(openstates_bill_id);