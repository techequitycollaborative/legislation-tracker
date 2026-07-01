--
-- PostgreSQL database dump
--

\restrict BPEOQ0z2pgwMrHzlAgP2rwQ2U4TZmGlRa2aMsrgBAlRswUPxfKpTVZbRvwZS4gT

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
-- Name: committee; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.committee (
    committee_id integer NOT NULL,
    chamber_id integer,
    name text,
    webpage_link text
);


ALTER TABLE snapshot.committee OWNER TO legtracker;

--
-- Name: committee_committee_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.committee_committee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.committee_committee_id_seq OWNER TO legtracker;

--
-- Name: committee_committee_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.committee_committee_id_seq OWNED BY snapshot.committee.committee_id;


--
-- Name: committee committee_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.committee ALTER COLUMN committee_id SET DEFAULT nextval('snapshot.committee_committee_id_seq'::regclass);


--
-- Name: committee committee_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.committee
    ADD CONSTRAINT committee_pkey PRIMARY KEY (committee_id);


--
-- Name: TABLE committee; Type: ACL; Schema: snapshot; Owner: legtracker
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE snapshot.committee TO dsherbini;


--
-- PostgreSQL database dump complete
--

\unrestrict BPEOQ0z2pgwMrHzlAgP2rwQ2U4TZmGlRa2aMsrgBAlRswUPxfKpTVZbRvwZS4gT

