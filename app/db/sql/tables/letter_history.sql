-- letter_history.sql
-- app.bill_letter_history: stores all versions of user-entered bill letters

-- Drop the table
DROP TABLE IF EXISTS app.bill_letter_history;

-- Table for letter history
CREATE TABLE app.bill_letter_history (
    id SERIAL PRIMARY KEY,
    openstates_bill_id VARCHAR(255) NOT NULL,
    bill_number VARCHAR(50) NOT NULL,
    org_id INTEGER NOT NULL,
    org_name VARCHAR(255) NOT NULL,
	letter_name VARCHAR(255) NOT NULL,
    letter_url TEXT NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    created_on DATE NOT NULL,
    created_at TIMESTAMP NOT NULL
);


-- Indexes for better query performance
CREATE INDEX idx_letter_history_bill_org ON app.bill_letter_history(openstates_bill_id, org_id);



