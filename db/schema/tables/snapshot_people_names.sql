--
-- PostgreSQL database dump
--

\restrict wokkZeFcuHNOUrPuE90LLKbhw5pf02zDMwq6JHUN8mzGuWCmnOcevUl7COeTgx1

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
-- Name: people_names; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people_names (
    people_name_id integer NOT NULL,
    openstates_people_id text,
    alt_name text
);


ALTER TABLE snapshot.people_names OWNER TO legtracker;

--
-- Name: people_names_people_name_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.people_names_people_name_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.people_names_people_name_id_seq OWNER TO legtracker;

--
-- Name: people_names_people_name_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.people_names_people_name_id_seq OWNED BY snapshot.people_names.people_name_id;


--
-- Name: people_names people_name_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_names ALTER COLUMN people_name_id SET DEFAULT nextval('snapshot.people_names_people_name_id_seq'::regclass);


--
-- Name: people_names people_names_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_names
    ADD CONSTRAINT people_names_pkey PRIMARY KEY (people_name_id);


--
-- PostgreSQL database dump complete
--

\unrestrict wokkZeFcuHNOUrPuE90LLKbhw5pf02zDMwq6JHUN8mzGuWCmnOcevUl7COeTgx1

