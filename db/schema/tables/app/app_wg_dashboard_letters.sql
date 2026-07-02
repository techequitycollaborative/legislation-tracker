--
-- PostgreSQL database dump
--

\restrict TVxqvptY6U4iHHhSMrKsW9UZbF4qPckjsBV6qhYGMFemXzX7SRgnMdMJDoKgwBm

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
-- Name: wg_dashboard_letters; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.wg_dashboard_letters (
    openstates_bill_id text,
    bill_number text,
    org_id integer,
    org_name character varying(255),
    letter_name character varying(255),
    letter_url text,
    created_on date,
    created_at timestamp without time zone
);


ALTER TABLE app.wg_dashboard_letters OWNER TO legtracker;

--
-- Name: idx_wg_dashboard_letters_bill; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wg_dashboard_letters_bill ON app.wg_dashboard_letters USING btree (openstates_bill_id);


--
-- Name: idx_wg_dashboard_letters_bill_org; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wg_dashboard_letters_bill_org ON app.wg_dashboard_letters USING btree (openstates_bill_id, org_id);


--
-- Name: idx_wg_dashboard_letters_org; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wg_dashboard_letters_org ON app.wg_dashboard_letters USING btree (org_id);


--
-- PostgreSQL database dump complete
--

\unrestrict TVxqvptY6U4iHHhSMrKsW9UZbF4qPckjsBV6qhYGMFemXzX7SRgnMdMJDoKgwBm

