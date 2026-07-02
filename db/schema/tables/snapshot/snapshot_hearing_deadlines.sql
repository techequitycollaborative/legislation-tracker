--
-- PostgreSQL database dump
--

\restrict BrkhjVWZ5tTDd8hI5C3Jz9bhzNUKQSfWuLjZszaNhDPQahsGwXoSf5Cqb9KOu7J

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
-- Name: hearing_deadlines; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.hearing_deadlines (
    id integer NOT NULL,
    hearing_id integer NOT NULL,
    deadline_date date NOT NULL,
    deadline_type character varying(100) DEFAULT 'letter'::character varying
);


ALTER TABLE snapshot.hearing_deadlines OWNER TO legtracker;

--
-- Name: hearing_deadlines_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.hearing_deadlines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.hearing_deadlines_id_seq OWNER TO legtracker;

--
-- Name: hearing_deadlines_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.hearing_deadlines_id_seq OWNED BY snapshot.hearing_deadlines.id;


--
-- Name: hearing_deadlines id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_deadlines ALTER COLUMN id SET DEFAULT nextval('snapshot.hearing_deadlines_id_seq'::regclass);


--
-- Name: hearing_deadlines hearing_deadlines_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_deadlines
    ADD CONSTRAINT hearing_deadlines_pkey PRIMARY KEY (id);


--
-- Name: hearing_deadlines unique_deadline; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_deadlines
    ADD CONSTRAINT unique_deadline UNIQUE (hearing_id, deadline_type);


--
-- Name: idx_hearing_deadlines_deadline_date; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearing_deadlines_deadline_date ON snapshot.hearing_deadlines USING btree (deadline_date);


--
-- Name: idx_hearing_deadlines_hearing_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearing_deadlines_hearing_id ON snapshot.hearing_deadlines USING btree (hearing_id);


--
-- Name: hearing_deadlines hearing_deadlines_hearing_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_deadlines
    ADD CONSTRAINT hearing_deadlines_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES snapshot.hearings(hearing_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict BrkhjVWZ5tTDd8hI5C3Jz9bhzNUKQSfWuLjZszaNhDPQahsGwXoSf5Cqb9KOu7J

