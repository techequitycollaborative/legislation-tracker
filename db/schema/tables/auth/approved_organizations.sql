--
-- PostgreSQL database dump
--

\restrict MDtf0uYmYcCSVAsV4f8mE58BgOXUalgBabg1qVQ9GnkC7X3zDgWXKhMb3fyY3De

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
-- Name: approved_organizations; Type: TABLE; Schema: auth; Owner: legtracker
--

CREATE TABLE auth.approved_organizations (
    id integer NOT NULL,
    name text NOT NULL,
    domain text,
    nickname text,
    feed_token_hash text,
    feed_token_created_at timestamp with time zone,
    feed_token text
);


ALTER TABLE auth.approved_organizations OWNER TO legtracker;

--
-- Name: approved_organizations_id_seq; Type: SEQUENCE; Schema: auth; Owner: legtracker
--

CREATE SEQUENCE auth.approved_organizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.approved_organizations_id_seq OWNER TO legtracker;

--
-- Name: approved_organizations_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: legtracker
--

ALTER SEQUENCE auth.approved_organizations_id_seq OWNED BY auth.approved_organizations.id;


--
-- Name: approved_organizations id; Type: DEFAULT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_organizations ALTER COLUMN id SET DEFAULT nextval('auth.approved_organizations_id_seq'::regclass);


--
-- Name: approved_organizations approved_organizations_feed_token_hash_key; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_organizations
    ADD CONSTRAINT approved_organizations_feed_token_hash_key UNIQUE (feed_token_hash);


--
-- Name: approved_organizations approved_organizations_pkey; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_organizations
    ADD CONSTRAINT approved_organizations_pkey PRIMARY KEY (id);


--
-- Name: idx_approved_orgs_feed_token; Type: INDEX; Schema: auth; Owner: legtracker
--

CREATE INDEX idx_approved_orgs_feed_token ON auth.approved_organizations USING btree (feed_token_hash) WHERE (feed_token_hash IS NOT NULL);


--
-- Name: TABLE approved_organizations; Type: ACL; Schema: auth; Owner: legtracker
--

REVOKE SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_organizations FROM legtracker;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_organizations TO legtracker WITH GRANT OPTION;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_organizations TO kschiedeck;


--
-- Name: SEQUENCE approved_organizations_id_seq; Type: ACL; Schema: auth; Owner: legtracker
--

GRANT ALL ON SEQUENCE auth.approved_organizations_id_seq TO kschiedeck;


--
-- PostgreSQL database dump complete
--

\unrestrict MDtf0uYmYcCSVAsV4f8mE58BgOXUalgBabg1qVQ9GnkC7X3zDgWXKhMb3fyY3De

