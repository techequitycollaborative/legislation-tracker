--
-- PostgreSQL database dump
--

\restrict I8nLtgFP5GDsLmYBGjWo1Tq7xA4xCUu2BLAIHHpshlYT5N6umlFBv12R3muAlAl

-- Dumped from database version 14.23
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: committee_assignment; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.committee_assignment (
    committee_assignment_id integer NOT NULL,
    committee_id integer NOT NULL,
    chamber_id integer NOT NULL,
    legislator_name character varying(255) NOT NULL,
    assignment_type character varying(50) NOT NULL,
    session character varying(20) DEFAULT '20252026'::character varying NOT NULL
);


ALTER TABLE snapshot.committee_assignment OWNER TO legtracker;

--
-- Name: committee_assignment_committee_assignment_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.committee_assignment_committee_assignment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.committee_assignment_committee_assignment_id_seq OWNER TO legtracker;

--
-- Name: committee_assignment_committee_assignment_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.committee_assignment_committee_assignment_id_seq OWNED BY snapshot.committee_assignment.committee_assignment_id;


--
-- Name: committee_assignment committee_assignment_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.committee_assignment ALTER COLUMN committee_assignment_id SET DEFAULT nextval('snapshot.committee_assignment_committee_assignment_id_seq'::regclass);


--
-- Name: committee_assignment committee_assignment_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.committee_assignment
    ADD CONSTRAINT committee_assignment_pkey PRIMARY KEY (committee_assignment_id);


--
-- Name: idx_committee_assignment_chamber_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_committee_assignment_chamber_id ON snapshot.committee_assignment USING btree (chamber_id);


--
-- Name: idx_committee_assignment_committee_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_committee_assignment_committee_id ON snapshot.committee_assignment USING btree (committee_id);


--
-- Name: idx_committee_assignment_legislator; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_committee_assignment_legislator ON snapshot.committee_assignment USING btree (legislator_name);


--
-- Name: idx_committee_assignment_session; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_committee_assignment_session ON snapshot.committee_assignment USING btree (session);


--
-- Name: committee_assignment committee_assignment_committee_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.committee_assignment
    ADD CONSTRAINT committee_assignment_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES snapshot.committee(committee_id);


--
-- PostgreSQL database dump complete
--

\unrestrict I8nLtgFP5GDsLmYBGjWo1Tq7xA4xCUu2BLAIHHpshlYT5N6umlFBv12R3muAlAl

