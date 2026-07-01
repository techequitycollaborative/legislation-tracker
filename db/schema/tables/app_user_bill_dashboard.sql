--
-- PostgreSQL database dump
--

\restrict Pme7rRgmncoNGva4naQOKaihr780fl9B2GkvuG2hjUOjV2wmmQ8VHfstd7B46pI

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
-- Name: user_bill_dashboard; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.user_bill_dashboard (
    user_bill_dashboard_id integer NOT NULL,
    user_email text,
    added_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    bill_number text,
    openstates_bill_id text,
    org_id integer
);


ALTER TABLE app.user_bill_dashboard OWNER TO legtracker;

--
-- Name: user_bill_dashboard_user_bill_dashboard_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.user_bill_dashboard_user_bill_dashboard_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.user_bill_dashboard_user_bill_dashboard_id_seq OWNER TO legtracker;

--
-- Name: user_bill_dashboard_user_bill_dashboard_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.user_bill_dashboard_user_bill_dashboard_id_seq OWNED BY app.user_bill_dashboard.user_bill_dashboard_id;


--
-- Name: user_bill_dashboard user_bill_dashboard_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.user_bill_dashboard ALTER COLUMN user_bill_dashboard_id SET DEFAULT nextval('app.user_bill_dashboard_user_bill_dashboard_id_seq'::regclass);


--
-- Name: user_bill_dashboard user_bill_dashboard_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.user_bill_dashboard
    ADD CONSTRAINT user_bill_dashboard_pkey PRIMARY KEY (user_bill_dashboard_id);


--
-- PostgreSQL database dump complete
--

\unrestrict Pme7rRgmncoNGva4naQOKaihr780fl9B2GkvuG2hjUOjV2wmmQ8VHfstd7B46pI

