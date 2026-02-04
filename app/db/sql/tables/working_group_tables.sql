-- working_group_tables.sql
-- Create table for the working group dashboard, which houses bills added to the wg dashboard
-- Create table for working group discussion board comments

-- Table: working_group_dashboard
CREATE TABLE app.working_group_dashboard (
    working_group_dashboard_id SERIAL PRIMARY KEY,
    added_by_org TEXT,       
    added_by_user TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	bill_number TEXT NOT NULL,
    openstates_bill_id TEXT     
);

-- Table: working_group_discussions
DROP TABLE IF EXISTS app.working_group_discussions;
CREATE TABLE app.working_group_discussions (
    comment_id SERIAL PRIMARY KEY,
    bill_number TEXT NOT NULL,
	user_name TEXT NOT NULL,
    user_email TEXT NOT NULL,
	org_id INT,
	org_name TEXT,
    comment TEXT NOT NULL,
	added_on DATE DEFAULT CURRENT_DATE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for working_group_discussions
CREATE INDEX idx_wgd_bill_number ON app.working_group_discussions(bill_number);
CREATE INDEX idx_wgd_user_name ON app.working_group_discussions(user_name);
CREATE INDEX idx_wgd_user_email ON app.working_group_discussions(user_email);
CREATE INDEX idx_wgd_org_id ON app.working_group_discussions(org_id);
CREATE INDEX idx_wgd_added_on ON app.working_group_discussions(added_on DESC);
CREATE INDEX idx_wgd_added_at ON app.working_group_discussions(added_at DESC);

-- Composite indexes for common query patterns
CREATE INDEX idx_wgd_bill_timestamp ON app.working_group_discussions(bill_number, added_at DESC);
CREATE INDEX idx_wgd_org_bill ON app.working_group_discussions(org_id, bill_number);


