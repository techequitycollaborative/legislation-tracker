--
-- PostgreSQL database dump
--

\restrict bSbQfNXMFXsO87oY1ybwav2p8Dt674gbarMEcCbFiSvdG4XRTouE55UJJsIC6ph

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
-- Name: people_offices; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people_offices (
    people_office_id integer NOT NULL,
    openstates_people_id text,
    name text,
    phone text,
    address text,
    classification text
);


ALTER TABLE snapshot.people_offices OWNER TO legtracker;

--
-- Name: people_offices_people_office_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.people_offices_people_office_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.people_offices_people_office_id_seq OWNER TO legtracker;

--
-- Name: people_offices_people_office_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.people_offices_people_office_id_seq OWNED BY snapshot.people_offices.people_office_id;


--
-- Name: people_offices people_office_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_offices ALTER COLUMN people_office_id SET DEFAULT nextval('snapshot.people_offices_people_office_id_seq'::regclass);


--
-- Name: people_offices people_offices_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_offices
    ADD CONSTRAINT people_offices_pkey PRIMARY KEY (people_office_id);


--
-- PostgreSQL database dump complete
--

\unrestrict bSbQfNXMFXsO87oY1ybwav2p8Dt674gbarMEcCbFiSvdG4XRTouE55UJJsIC6ph

