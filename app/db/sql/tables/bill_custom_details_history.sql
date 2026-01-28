-- bill_custom_details_history.sql
-- Creates a table for storing changes in user-entered bill custom fields.

DROP TABLE IF EXISTS app.bill_custom_details_history;

CREATE TABLE app.bill_custom_details_history (
    history_id SERIAL PRIMARY KEY,
    openstates_bill_id TEXT NOT NULL,
    bill_number TEXT,
    org_id INT,
    org_name TEXT,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT NOT NULL,
    changed_on DATE DEFAULT CURRENT_DATE,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster queries
CREATE INDEX idx_history_bill_org ON app.bill_custom_details_history(openstates_bill_id, org_id);
CREATE INDEX idx_history_timestamp ON app.bill_custom_details_history(changed_at DESC);
CREATE INDEX idx_history_user ON app.bill_custom_details_history(changed_by);
CREATE INDEX idx_history_field ON app.bill_custom_details_history(field_name);