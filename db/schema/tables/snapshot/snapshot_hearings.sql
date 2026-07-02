--
-- PostgreSQL database dump
--

\restrict BjxEJAhgITXl3cKewEa4Efo0MPYjuSKAtgvNnOxA9ydcwae8wBf8cH8LbgX6rfX

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
-- Name: hearings; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.hearings (
    hearing_id integer NOT NULL,
    committee_id integer,
    name character varying(150) NOT NULL,
    date date NOT NULL,
    time_verbatim character varying(100),
    time_normalized time without time zone,
    is_allday boolean DEFAULT false NOT NULL,
    location character varying NOT NULL,
    room character varying,
    notes text,
    chamber_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    canceled_at timestamp with time zone
);


ALTER TABLE snapshot.hearings OWNER TO legtracker;

--
-- Name: hearings_hearing_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.hearings_hearing_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.hearings_hearing_id_seq OWNER TO legtracker;

--
-- Name: hearings_hearing_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.hearings_hearing_id_seq OWNED BY snapshot.hearings.hearing_id;


--
-- Name: hearings hearing_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearings ALTER COLUMN hearing_id SET DEFAULT nextval('snapshot.hearings_hearing_id_seq'::regclass);


--
-- Name: hearings hearings_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearings
    ADD CONSTRAINT hearings_pkey PRIMARY KEY (hearing_id);


--
-- Name: hearings uq_hearings_chamber_name_date_time; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearings
    ADD CONSTRAINT uq_hearings_chamber_name_date_time UNIQUE (chamber_id, name, date, time_verbatim);


--
-- Name: idx_hearings_chamber_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearings_chamber_id ON snapshot.hearings USING btree (chamber_id);


--
-- Name: idx_hearings_committee_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearings_committee_id ON snapshot.hearings USING btree (committee_id);


--
-- Name: idx_hearings_date; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearings_date ON snapshot.hearings USING btree (date);


--
-- Name: hearings trg_hearings_updated_at; Type: TRIGGER; Schema: snapshot; Owner: legtracker
--

CREATE TRIGGER trg_hearings_updated_at BEFORE UPDATE ON snapshot.hearings FOR EACH ROW EXECUTE FUNCTION snapshot.update_hearing_updated_at();


--
-- Name: hearings hearings_chamber_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearings
    ADD CONSTRAINT hearings_chamber_id_fkey FOREIGN KEY (chamber_id) REFERENCES snapshot.chamber(chamber_id);


--
-- Name: hearings hearings_committee_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearings
    ADD CONSTRAINT hearings_committee_id_fkey FOREIGN KEY (committee_id) REFERENCES snapshot.committee(committee_id);


--
-- PostgreSQL database dump complete
--

\unrestrict BjxEJAhgITXl3cKewEa4Efo0MPYjuSKAtgvNnOxA9ydcwae8wBf8cH8LbgX6rfX

