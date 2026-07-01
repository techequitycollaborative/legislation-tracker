--
-- PostgreSQL database dump
--

\restrict uuMnQMbWI3Jcqw8dxALogz1gP9KR5PKwTrwzErVJN5Gbd7zP3BuQOUQZoCXwYZV

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
-- Name: chamber; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.chamber (
    chamber_id integer NOT NULL,
    chamber_name text NOT NULL
);


ALTER TABLE snapshot.chamber OWNER TO legtracker;

--
-- Name: chamber_chamber_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.chamber_chamber_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.chamber_chamber_id_seq OWNER TO legtracker;

--
-- Name: chamber_chamber_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.chamber_chamber_id_seq OWNED BY snapshot.chamber.chamber_id;


--
-- Name: chamber chamber_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.chamber ALTER COLUMN chamber_id SET DEFAULT nextval('snapshot.chamber_chamber_id_seq'::regclass);


--
-- Name: chamber chamber_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.chamber
    ADD CONSTRAINT chamber_pkey PRIMARY KEY (chamber_id);


--
-- PostgreSQL database dump complete
--

\unrestrict uuMnQMbWI3Jcqw8dxALogz1gP9KR5PKwTrwzErVJN5Gbd7zP3BuQOUQZoCXwYZV

