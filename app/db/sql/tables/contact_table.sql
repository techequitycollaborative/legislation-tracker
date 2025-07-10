-- contact_table.sql
-- Store custom details for a legislator's issue area

-- Table: contact_custom_details -- this table stores custom details for legislator contacts (rendered on legislator page)
CREATE TABLE IF NOT EXISTS contact_custom_details (
    contact_custom_details_id SERIAL PRIMARY KEY,
    openstates_people_id TEXT NOT NULL, -- used for selecting all custom contacts
    people_contact_id INT UNIQUE, -- foreign key from snapshot.people_contacts
    custom_staffer_contact TEXT NOT NULL,
    custom_staffer_email TEXT NOT NULL,
    last_updated_by TEXT,
    last_updated_org_id INT,
    last_updated_org_name TEXT,
    last_updated_on DATE,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);