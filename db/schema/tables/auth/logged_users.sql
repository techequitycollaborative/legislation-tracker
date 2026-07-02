--
-- PostgreSQL database dump
--

\restrict PYKsZ3VEd5CbYiwjI5ahqqQrYaf67GAeRUGTQLlhsXdbTx1txbg0BfwqBncA2Zc

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
-- Name: logged_users; Type: TABLE; Schema: auth; Owner: legtracker
--

CREATE TABLE auth.logged_users (
    id integer NOT NULL,
    name text,
    email text,
    password_hash text,
    org_id integer NOT NULL,
    created_at timestamp with time zone,
    last_login timestamp with time zone
);


ALTER TABLE auth.logged_users OWNER TO legtracker;

--
-- Name: logged_users_id_seq; Type: SEQUENCE; Schema: auth; Owner: legtracker
--

CREATE SEQUENCE auth.logged_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.logged_users_id_seq OWNER TO legtracker;

--
-- Name: logged_users_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: legtracker
--

ALTER SEQUENCE auth.logged_users_id_seq OWNED BY auth.logged_users.id;


--
-- Name: logged_users id; Type: DEFAULT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logged_users ALTER COLUMN id SET DEFAULT nextval('auth.logged_users_id_seq'::regclass);


--
-- Name: logged_users logged_users_pkey; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logged_users
    ADD CONSTRAINT logged_users_pkey PRIMARY KEY (id);


--
-- Name: logged_users logged_users_org_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.logged_users
    ADD CONSTRAINT logged_users_org_id_fkey FOREIGN KEY (org_id) REFERENCES auth.approved_organizations(id);


--
-- Name: TABLE logged_users; Type: ACL; Schema: auth; Owner: legtracker
--

REVOKE SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.logged_users FROM legtracker;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.logged_users TO legtracker WITH GRANT OPTION;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.logged_users TO kschiedeck;


--
-- Name: SEQUENCE logged_users_id_seq; Type: ACL; Schema: auth; Owner: legtracker
--

GRANT ALL ON SEQUENCE auth.logged_users_id_seq TO kschiedeck;


--
-- PostgreSQL database dump complete
--

\unrestrict PYKsZ3VEd5CbYiwjI5ahqqQrYaf67GAeRUGTQLlhsXdbTx1txbg0BfwqBncA2Zc

