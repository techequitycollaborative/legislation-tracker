--
-- PostgreSQL database dump
--

\restrict ZYumhUuDQMJ7fPNfeYh0KWEQMgVbgR6JNIvW1ffDhgwO1vRWX1krrBhit4t2qnb

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
-- Name: working_group_dashboard; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.working_group_dashboard (
    working_group_dashboard_id integer NOT NULL,
    added_by_org text,
    added_by_user text,
    added_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    bill_number text NOT NULL,
    openstates_bill_id text
);


ALTER TABLE app.working_group_dashboard OWNER TO legtracker;

--
-- Name: working_group_dashboard_working_group_dashboard_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.working_group_dashboard_working_group_dashboard_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.working_group_dashboard_working_group_dashboard_id_seq OWNER TO legtracker;

--
-- Name: working_group_dashboard_working_group_dashboard_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.working_group_dashboard_working_group_dashboard_id_seq OWNED BY app.working_group_dashboard.working_group_dashboard_id;


--
-- Name: working_group_dashboard working_group_dashboard_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.working_group_dashboard ALTER COLUMN working_group_dashboard_id SET DEFAULT nextval('app.working_group_dashboard_working_group_dashboard_id_seq'::regclass);


--
-- Name: working_group_dashboard working_group_dashboard_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.working_group_dashboard
    ADD CONSTRAINT working_group_dashboard_pkey PRIMARY KEY (working_group_dashboard_id);


--
-- PostgreSQL database dump complete
--

\unrestrict ZYumhUuDQMJ7fPNfeYh0KWEQMgVbgR6JNIvW1ffDhgwO1vRWX1krrBhit4t2qnb

