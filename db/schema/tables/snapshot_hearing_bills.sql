--
-- PostgreSQL database dump
--

\restrict rdJRhN9Xm41VBkIZef8xVODCYPNhbaX5MJGQKzYFQuDldKWrklxTkAEjEdOEOMB

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
-- Name: hearing_bills; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.hearing_bills (
    id integer NOT NULL,
    hearing_id integer NOT NULL,
    openstates_bill_id character varying(50) NOT NULL,
    file_order integer NOT NULL,
    footnote text,
    footnote_symbol character(1) DEFAULT NULL::bpchar
);


ALTER TABLE snapshot.hearing_bills OWNER TO legtracker;

--
-- Name: hearing_bills_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.hearing_bills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.hearing_bills_id_seq OWNER TO legtracker;

--
-- Name: hearing_bills_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.hearing_bills_id_seq OWNED BY snapshot.hearing_bills.id;


--
-- Name: hearing_bills id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_bills ALTER COLUMN id SET DEFAULT nextval('snapshot.hearing_bills_id_seq'::regclass);


--
-- Name: hearing_bills hearing_bills_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_bills
    ADD CONSTRAINT hearing_bills_pkey PRIMARY KEY (id);


--
-- Name: hearing_bills uq_hearing_bills_hearing_bill; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_bills
    ADD CONSTRAINT uq_hearing_bills_hearing_bill UNIQUE (hearing_id, openstates_bill_id);


--
-- Name: idx_hearing_bills_bill_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearing_bills_bill_id ON snapshot.hearing_bills USING btree (openstates_bill_id);


--
-- Name: idx_hearing_bills_hearing_id; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX idx_hearing_bills_hearing_id ON snapshot.hearing_bills USING btree (hearing_id);


--
-- Name: hearing_bills trg_hearing_bills_touch_parent; Type: TRIGGER; Schema: snapshot; Owner: legtracker
--

CREATE TRIGGER trg_hearing_bills_touch_parent AFTER INSERT OR DELETE OR UPDATE ON snapshot.hearing_bills FOR EACH ROW EXECUTE FUNCTION snapshot.touch_hearing_on_bill_change();


--
-- Name: hearing_bills hearing_bills_hearing_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.hearing_bills
    ADD CONSTRAINT hearing_bills_hearing_id_fkey FOREIGN KEY (hearing_id) REFERENCES snapshot.hearings(hearing_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict rdJRhN9Xm41VBkIZef8xVODCYPNhbaX5MJGQKzYFQuDldKWrklxTkAEjEdOEOMB

