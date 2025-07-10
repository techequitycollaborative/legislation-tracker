-- working_group_tables.sql
-- Create table for the working group dashboard
-- Create table for working group discussion board comments

-- Table: working_group_dashboard
CREATE TABLE public.working_group_dashboard (
    working_group_dashboard_id SERIAL PRIMARY KEY,
    added_by_org TEXT,       
    added_by_user TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	bill_number TEXT NOT NULL,
    openstates_bill_id TEXT     
);

-- Table: working_group_discussions
CREATE TABLE public.working_group_discussions (
    id SERIAL PRIMARY KEY,
    bill_number TEXT NOT NULL,
    user_email TEXT NOT NULL,
    comment TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reply_to INTEGER REFERENCES public.working_group_discussions(id) ON DELETE CASCADE
);

