-- topic_tables.sql
-- Create all tables for leg tracker topic assignment.

-- Extension: pgvector for embedding storage
CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS snapshot.topic_embedding CASCADE;
DROP TABLE IF EXISTS snapshot.bill_embedding CASCADE;
DROP TABLE IF EXISTS snapshot.bill_topics CASCADE;

-- Table: snapshot.topic_embedding
CREATE TABLE IF NOT EXISTS snapshot.topic_embedding (
    topic_id SERIAL PRIMARY KEY,
    topic_phrase TEXT UNIQUE NOT NULL,
    keywords TEXT[],
    embedding vector(384),
    embedding_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: snapshot.bill_embedding
CREATE TABLE IF NOT EXISTS snapshot.bill_embedding (
    openstates_bill_id TEXT REFERENCES snapshot.bill(openstates_bill_id) PRIMARY KEY,
    weighted_embedding vector(384),
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: snapshot.bill_topics
CREATE TABLE snapshot.bill_topics (
    openstates_bill_id TEXT REFERENCES snapshot.bill(openstates_bill_id),
    topic_phrase TEXT REFERENCES snapshot.topic_embedding(topic_phrase),
    match_method TEXT NOT NULL CHECK (match_method IN ('keyword', 'similarity')),
    similarity FLOAT,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for fast timestamp queries
CREATE INDEX ON snapshot.topic_embedding (embedding_updated_at);
CREATE INDEX ON snapshot.bill_embedding (computed_at);
CREATE INDEX ON snapshot.bill_topics (assigned_at);
