--
-- PostgreSQL database dump
--

\restrict KQzNnY5X8wvJahzr1JBAgeX6ccfK8HnhZ3feyp4qiWwhZVPmftyF6TqpsaiZDh3

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
-- Name: contact_custom_details; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.contact_custom_details (
    contact_custom_details_id integer NOT NULL,
    openstates_people_id text NOT NULL,
    people_contact_id integer,
    custom_staffer_contact text NOT NULL,
    custom_staffer_email text NOT NULL,
    last_updated_by text,
    last_updated_org_id integer,
    last_updated_org_name text,
    last_updated_on date,
    last_updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.contact_custom_details OWNER TO legtracker;

--
-- Name: contact_custom_details_contact_custom_details_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.contact_custom_details_contact_custom_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.contact_custom_details_contact_custom_details_id_seq OWNER TO legtracker;

--
-- Name: contact_custom_details_contact_custom_details_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.contact_custom_details_contact_custom_details_id_seq OWNED BY app.contact_custom_details.contact_custom_details_id;


--
-- Name: contact_custom_details contact_custom_details_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.contact_custom_details ALTER COLUMN contact_custom_details_id SET DEFAULT nextval('app.contact_custom_details_contact_custom_details_id_seq'::regclass);


--
-- Name: contact_custom_details contact_custom_details_people_contact_id_key; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.contact_custom_details
    ADD CONSTRAINT contact_custom_details_people_contact_id_key UNIQUE (people_contact_id);


--
-- Name: contact_custom_details contact_custom_details_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.contact_custom_details
    ADD CONSTRAINT contact_custom_details_pkey PRIMARY KEY (contact_custom_details_id);


--
-- PostgreSQL database dump complete
--

\unrestrict KQzNnY5X8wvJahzr1JBAgeX6ccfK8HnhZ3feyp4qiWwhZVPmftyF6TqpsaiZDh3

