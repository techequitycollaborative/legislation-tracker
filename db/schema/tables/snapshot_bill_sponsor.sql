--
-- PostgreSQL database dump
--

\restrict jAQIdOgMiVwKLV6YOjpJOXSNzV2kTvOG8Eks8faAMiR40q5NUAdOWJ0dgV0yM9J

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
-- Name: bill_sponsor; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.bill_sponsor (
    openstates_bill_id text,
    name text,
    full_name text,
    title text,
    district text,
    primary_author text,
    type text
);


ALTER TABLE snapshot.bill_sponsor OWNER TO legtracker;

--
-- Name: TABLE bill_sponsor; Type: ACL; Schema: snapshot; Owner: legtracker
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE snapshot.bill_sponsor TO dsherbini;


--
-- PostgreSQL database dump complete
--

\unrestrict jAQIdOgMiVwKLV6YOjpJOXSNzV2kTvOG8Eks8faAMiR40q5NUAdOWJ0dgV0yM9J

