--
-- PostgreSQL database dump
--

\restrict yiTnlb5bSu3uhUGUcTCkw7yDFlFCbaFgVWqPu5jUYDRwlRw4xshnnzeWXOO16s8

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
-- Name: people_contacts; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people_contacts (
    people_contact_id integer NOT NULL,
    openstates_people_id text,
    staffer_contact text,
    generated_email text,
    issue_area text,
    staffer_type text
);


ALTER TABLE snapshot.people_contacts OWNER TO legtracker;

--
-- Name: people_contacts_people_contact_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.people_contacts_people_contact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.people_contacts_people_contact_id_seq OWNER TO legtracker;

--
-- Name: people_contacts_people_contact_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.people_contacts_people_contact_id_seq OWNED BY snapshot.people_contacts.people_contact_id;


--
-- Name: people_contacts people_contact_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_contacts ALTER COLUMN people_contact_id SET DEFAULT nextval('snapshot.people_contacts_people_contact_id_seq'::regclass);


--
-- Name: people_contacts people_contacts_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_contacts
    ADD CONSTRAINT people_contacts_pkey PRIMARY KEY (people_contact_id);


--
-- PostgreSQL database dump complete
--

\unrestrict yiTnlb5bSu3uhUGUcTCkw7yDFlFCbaFgVWqPu5jUYDRwlRw4xshnnzeWXOO16s8

