--
-- PostgreSQL database dump
--

\restrict bCoT1jtsgfREcVKgf9CsnrLYd7PD7DeOtTpSAWbeleHu4jev7s53e8gMtKJq34e

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
-- Name: bill_letter_history; Type: TABLE; Schema: app; Owner: legtracker
--

CREATE TABLE app.bill_letter_history (
    id integer NOT NULL,
    openstates_bill_id character varying(255) NOT NULL,
    bill_number character varying(50) NOT NULL,
    org_id integer NOT NULL,
    org_name character varying(255) NOT NULL,
    letter_name character varying(255) NOT NULL,
    letter_url text NOT NULL,
    created_by character varying(255) NOT NULL,
    created_on date NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE app.bill_letter_history OWNER TO legtracker;

--
-- Name: bill_letter_history_id_seq; Type: SEQUENCE; Schema: app; Owner: legtracker
--

CREATE SEQUENCE app.bill_letter_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.bill_letter_history_id_seq OWNER TO legtracker;

--
-- Name: bill_letter_history_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: legtracker
--

ALTER SEQUENCE app.bill_letter_history_id_seq OWNED BY app.bill_letter_history.id;


--
-- Name: bill_letter_history id; Type: DEFAULT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_letter_history ALTER COLUMN id SET DEFAULT nextval('app.bill_letter_history_id_seq'::regclass);


--
-- Name: bill_letter_history bill_letter_history_pkey; Type: CONSTRAINT; Schema: app; Owner: legtracker
--

ALTER TABLE ONLY app.bill_letter_history
    ADD CONSTRAINT bill_letter_history_pkey PRIMARY KEY (id);


--
-- Name: idx_letter_history_bill_org; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_letter_history_bill_org ON app.bill_letter_history USING btree (openstates_bill_id, org_id);


--
-- PostgreSQL database dump complete
--

\unrestrict bCoT1jtsgfREcVKgf9CsnrLYd7PD7DeOtTpSAWbeleHu4jev7s53e8gMtKJq34e

