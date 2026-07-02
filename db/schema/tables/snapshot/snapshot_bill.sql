--
-- PostgreSQL database dump
--

\restrict QedTo6X0tOreFUQnVHw2EZIrZOP1liqmAg6hF6vQOBhTJQ9TBg5egJFGbfpEhpX

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
-- Name: bill; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.bill (
    openstates_bill_id text NOT NULL,
    session text,
    chamber text,
    bill_num text,
    title text,
    created_at text,
    updated_at text,
    first_action_date text,
    last_action_date text,
    abstract text
);


ALTER TABLE snapshot.bill OWNER TO legtracker;

--
-- Name: bill bill_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.bill
    ADD CONSTRAINT bill_pkey PRIMARY KEY (openstates_bill_id);


--
-- Name: TABLE bill; Type: ACL; Schema: snapshot; Owner: legtracker
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE snapshot.bill TO dsherbini;


--
-- PostgreSQL database dump complete
--

\unrestrict QedTo6X0tOreFUQnVHw2EZIrZOP1liqmAg6hF6vQOBhTJQ9TBg5egJFGbfpEhpX

