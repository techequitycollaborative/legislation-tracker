-- calendar_tables.sql
-- Create all tables for leg tracker calendar v2.0 feature

-- Table: chamber
CREATE TABLE IF NOT EXISTS snapshot.chamber (
    chamber_id SERIAL PRIMARY KEY,
    chamber_name TEXT NOT NULL
);
-- 
INSERT INTO snapshot.chamber (chamber_id, chamber_name)
VALUES
(1, 'Assembly'),
(2, 'Senate'),
(3, 'Joint');

-- Table: hearings
-- hearing_id (PK), committee_id (FK), date, time, name, location, notes, chamber_id (FK), created_at, updated_at
CREATE TABLE IF NOT EXISTS snapshot.hearings (
    hearing_id SERIAL PRIMARY KEY,
    committee_id INT REFERENCES snapshot.committee(committee_id) NULL,
    date DATE NOT NULL,
    time_verbatim VARCHAR(50), -- verbatim string from website
    time_normalized TIME, -- null if is_allday
    is_allday BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(100) NOT NULL, -- address
    room VARCHAR(100), -- if applicable
    notes TEXT,
    chamber_id INTEGER REFERENCES snapshot.chamber(chamber_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_hearings_date ON snapshot.hearings(date);
CREATE INDEX idx_hearings_chamber_id ON snapshot.hearings(chamber_id);
CREATE INDEX idx_hearings_committee_id ON snapshot.hearings(committee_id);

-- Table: hearing_bills
-- id (PK), hearing_id (FK), bill_id (FK), file_order, created_at, updated_at
-- Indexed on hearing_id and bill_id for query performance
CREATE TABLE IF NOT EXISTS snapshot.hearing_bills (
    id SERIAL PRIMARY KEY,
    hearing_id INT NOT NULL REFERENCES snapshot.hearings(hearing_id) ON DELETE CASCADE,
    openstates_bill_id VARCHAR(50) NOT NULL,  -- openstates_bill_id format
    file_order INTEGER NOT NULL
);

CREATE INDEX idx_hearing_bills_hearing_id ON snapshot.hearing_bills(hearing_id);
CREATE INDEX idx_hearing_bills_bill_id ON snapshot.hearing_bills(openstates_bill_id);

-- Table: hearing_deadlines
-- id (PK), hearing_id (FK), bill_id (FK), deadline_date, deadline_type, created_at, updated_at
-- Indexed on hearing_id and bill_id for query performance
CREATE TABLE IF NOT EXISTS snapshot.hearing_deadlines (
    id SERIAL PRIMARY KEY,
    hearing_id INT NOT NULL REFERENCES snapshot.hearings(hearing_id) ON DELETE CASCADE,
    deadline_date DATE NOT NULL,
    deadline_type VARCHAR(100) DEFAULT 'letter',  -- e.g. 'testimony_prep', 'analysis'
    CONSTRAINT unique_deadline UNIQUE(hearing_id, deadline_type)
);

CREATE INDEX idx_hearing_deadlines_hearing_id ON snapshot.hearing_deadlines(hearing_id);
CREATE INDEX idx_hearing_deadlines_deadline_date ON snapshot.hearing_deadlines(deadline_date);