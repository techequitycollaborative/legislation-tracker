--
-- PostgreSQL database dump
--

\restrict k3GGCZKg3bN7tOuilnpVAs3nxhGL1vBOC6cKYMvZuwOXXeEIM4NeZ9oopix7adC

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
-- Name: logins; Type: TABLE; Schema: auth; Owner: legtracker
--

CREATE TABLE auth.logins (
    login_id integer NOT NULL,
    login_date date NOT NULL,
    login_time time without time zone NOT NULL,
    user_id integer,
    name text,
    email text,
    org text,
    org_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE auth.logins OWNER TO legtracker;

--
-- Name: logins_login_id_seq; Type: SEQUENCE; Schema: auth; Owner: legtracker
--

CREATE SEQUENCE auth.logins_login_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.logins_login_id_seq OWNER TO legtracker;

--
-- Name: logins_login_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: legtracker
--

ALTER SEQUENCE auth.logins_login_id_seq OWNED BY auth.logins.login_id;


--
-- Name: logins login_id; Type: DEFAULT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logins ALTER COLUMN login_id SET DEFAULT nextval('auth.logins_login_id_seq'::regclass);


--
-- Name: logins logins_pkey; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logins
    ADD CONSTRAINT logins_pkey PRIMARY KEY (login_id);


--
-- Name: logins logins_org_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logins
    ADD CONSTRAINT logins_org_id_fkey FOREIGN KEY (org_id) REFERENCES auth.approved_organizations(id);


--
-- Name: TABLE logins; Type: ACL; Schema: auth; Owner: legtracker
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.logins TO kschiedeck;


--
-- Name: SEQUENCE logins_login_id_seq; Type: ACL; Schema: auth; Owner: legtracker
--

GRANT ALL ON SEQUENCE auth.logins_login_id_seq TO kschiedeck;


--
-- PostgreSQL database dump complete
--

\unrestrict k3GGCZKg3bN7tOuilnpVAs3nxhGL1vBOC6cKYMvZuwOXXeEIM4NeZ9oopix7adC

