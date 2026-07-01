--
-- PostgreSQL database dump
--

\restrict Xyd6088NTMKLopvh69SbPd0w19HIn00kMtyaMN1FVFKZgsqnOdtFmjZEgEiCyuq

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
-- Name: bill_custom_details; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.bill_custom_details (
    bill_custom_details_id integer NOT NULL,
    bill_number text,
    org_position text,
    priority_tier text,
    community_sponsor text,
    coalition text,
    letter_of_support text,
    openstates_bill_id text,
    assigned_to text,
    action_taken text,
    last_updated_by text,
    last_updated_org_id integer,
    last_updated_org_name text,
    last_updated_on date,
    last_updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.bill_custom_details OWNER TO legtracker;

--
-- Name: bill_custom_details_bill_custom_details_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.bill_custom_details_bill_custom_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.bill_custom_details_bill_custom_details_id_seq OWNER TO legtracker;

--
-- Name: bill_custom_details_bill_custom_details_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.bill_custom_details_bill_custom_details_id_seq OWNED BY app.bill_custom_details.bill_custom_details_id;


--
-- Name: bill_custom_details bill_custom_details_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_custom_details ALTER COLUMN bill_custom_details_id SET DEFAULT nextval('app.bill_custom_details_bill_custom_details_id_seq'::regclass);


--
-- Name: bill_custom_details bill_custom_details_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_custom_details
    ADD CONSTRAINT bill_custom_details_pkey PRIMARY KEY (bill_custom_details_id);


--
-- Name: idx_bill_custom_details_bill_id; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_bill_custom_details_bill_id ON app.bill_custom_details USING btree (openstates_bill_id);


--
-- Name: idx_bill_custom_details_bill_org; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_bill_custom_details_bill_org ON app.bill_custom_details USING btree (openstates_bill_id, last_updated_org_id);


--
-- PostgreSQL database dump complete
--

\unrestrict Xyd6088NTMKLopvh69SbPd0w19HIn00kMtyaMN1FVFKZgsqnOdtFmjZEgEiCyuq

