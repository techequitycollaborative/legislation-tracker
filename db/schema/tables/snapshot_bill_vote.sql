--
-- PostgreSQL database dump
--

\restrict ipINXDiFNYhhuHN6qqGVDrr2EtQpc2YoEB2ypxF26glcytcksM3Wio5AsKGC9fz

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
-- Name: bill_vote; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.bill_vote (
    openstates_bill_id text,
    motion_text text,
    vote_date text,
    vote_location text,
    vote_result text,
    vote_threshold text,
    yes_count text,
    no_count text,
    other_count text
);


ALTER TABLE snapshot.bill_vote OWNER TO legtracker;

--
-- Name: TABLE bill_vote; Type: ACL; Schema: snapshot; Owner: legtracker
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE snapshot.bill_vote TO dsherbini;


--
-- PostgreSQL database dump complete
--

\unrestrict ipINXDiFNYhhuHN6qqGVDrr2EtQpc2YoEB2ypxF26glcytcksM3Wio5AsKGC9fz

