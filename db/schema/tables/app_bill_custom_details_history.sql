--
-- PostgreSQL database dump
--

\restrict 4MTu6igd3pwBeU7jvLac0OazjEWN5au70isa0t2TgRLH9zCqP3NUhKV4ztqxEgl

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
-- Name: bill_custom_details_history; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.bill_custom_details_history (
    history_id integer NOT NULL,
    openstates_bill_id text NOT NULL,
    bill_number text,
    org_id integer,
    org_name text,
    field_name text NOT NULL,
    old_value text,
    new_value text,
    changed_by text NOT NULL,
    changed_on date DEFAULT CURRENT_DATE,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.bill_custom_details_history OWNER TO legtracker;

--
-- Name: bill_custom_details_history_history_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.bill_custom_details_history_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.bill_custom_details_history_history_id_seq OWNER TO legtracker;

--
-- Name: bill_custom_details_history_history_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.bill_custom_details_history_history_id_seq OWNED BY app.bill_custom_details_history.history_id;


--
-- Name: bill_custom_details_history history_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_custom_details_history ALTER COLUMN history_id SET DEFAULT nextval('app.bill_custom_details_history_history_id_seq'::regclass);


--
-- Name: bill_custom_details_history bill_custom_details_history_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_custom_details_history
    ADD CONSTRAINT bill_custom_details_history_pkey PRIMARY KEY (history_id);


--
-- Name: idx_history_bill_org; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_history_bill_org ON app.bill_custom_details_history USING btree (openstates_bill_id, org_id);


--
-- Name: idx_history_field; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_history_field ON app.bill_custom_details_history USING btree (field_name);


--
-- Name: idx_history_timestamp; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_history_timestamp ON app.bill_custom_details_history USING btree (changed_at DESC);


--
-- Name: idx_history_user; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_history_user ON app.bill_custom_details_history USING btree (changed_by);


--
-- PostgreSQL database dump complete
--

\unrestrict 4MTu6igd3pwBeU7jvLac0OazjEWN5au70isa0t2TgRLH9zCqP3NUhKV4ztqxEgl

