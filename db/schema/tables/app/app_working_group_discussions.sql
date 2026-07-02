--
-- PostgreSQL database dump
--

\restrict yG1mrdQVeIxqkpHwSwhoCfy01sdxtWBd8SNpt6N3sKXbTWQNfeeVbhfGgdUAkJ5

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
-- Name: working_group_discussions; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.working_group_discussions (
    comment_id integer NOT NULL,
    bill_number text NOT NULL,
    user_name text NOT NULL,
    user_email text NOT NULL,
    org_id integer,
    org_name text,
    comment text NOT NULL,
    added_on date DEFAULT CURRENT_DATE,
    added_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.working_group_discussions OWNER TO legtracker;

--
-- Name: working_group_discussions_comment_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.working_group_discussions_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.working_group_discussions_comment_id_seq OWNER TO legtracker;

--
-- Name: working_group_discussions_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.working_group_discussions_comment_id_seq OWNED BY app.working_group_discussions.comment_id;


--
-- Name: working_group_discussions comment_id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.working_group_discussions ALTER COLUMN comment_id SET DEFAULT nextval('app.working_group_discussions_comment_id_seq'::regclass);


--
-- Name: working_group_discussions working_group_discussions_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.working_group_discussions
    ADD CONSTRAINT working_group_discussions_pkey PRIMARY KEY (comment_id);


--
-- Name: idx_wgd_added_at; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_added_at ON app.working_group_discussions USING btree (added_at DESC);


--
-- Name: idx_wgd_added_on; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_added_on ON app.working_group_discussions USING btree (added_on DESC);


--
-- Name: idx_wgd_bill_number; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_bill_number ON app.working_group_discussions USING btree (bill_number);


--
-- Name: idx_wgd_bill_timestamp; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_bill_timestamp ON app.working_group_discussions USING btree (bill_number, added_at DESC);


--
-- Name: idx_wgd_org_bill; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_org_bill ON app.working_group_discussions USING btree (org_id, bill_number);


--
-- Name: idx_wgd_org_id; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_org_id ON app.working_group_discussions USING btree (org_id);


--
-- Name: idx_wgd_user_email; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_user_email ON app.working_group_discussions USING btree (user_email);


--
-- Name: idx_wgd_user_name; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_wgd_user_name ON app.working_group_discussions USING btree (user_name);


--
-- PostgreSQL database dump complete
--

\unrestrict yG1mrdQVeIxqkpHwSwhoCfy01sdxtWBd8SNpt6N3sKXbTWQNfeeVbhfGgdUAkJ5

