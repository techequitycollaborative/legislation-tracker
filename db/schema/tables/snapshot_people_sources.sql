--
-- PostgreSQL database dump
--

\restrict i08xYlWKryYuFKjTIbFEd02JDuhOSBsgw2dKESjJZpLYijN6zeVkKtzifJcP0eU

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
-- Name: people_sources; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people_sources (
    people_source_id integer NOT NULL,
    openstates_people_id text,
    source_url text
);


ALTER TABLE snapshot.people_sources OWNER TO legtracker;

--
-- Name: people_sources_people_source_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.people_sources_people_source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.people_sources_people_source_id_seq OWNER TO legtracker;

--
-- Name: people_sources_people_source_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.people_sources_people_source_id_seq OWNED BY snapshot.people_sources.people_source_id;


--
-- Name: people_sources people_source_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_sources ALTER COLUMN people_source_id SET DEFAULT nextval('snapshot.people_sources_people_source_id_seq'::regclass);


--
-- Name: people_sources people_sources_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_sources
    ADD CONSTRAINT people_sources_pkey PRIMARY KEY (people_source_id);


--
-- PostgreSQL database dump complete
--

\unrestrict i08xYlWKryYuFKjTIbFEd02JDuhOSBsgw2dKESjJZpLYijN6zeVkKtzifJcP0eU

