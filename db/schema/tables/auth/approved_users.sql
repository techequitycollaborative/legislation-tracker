--
-- PostgreSQL database dump
--

\restrict uxY735DlXQfn3MlUAkh1TZHR1ewhYn1HWcBtv8SsIh1LJTtF77Y1rB5nO5Euw4c

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
-- Name: approved_users; Type: TABLE; Schema: auth; Owner: legtracker
--

CREATE TABLE auth.approved_users (
    approved_user_id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    org_name character varying(100),
    user_role character varying(20),
    ai_working_group character varying(3) DEFAULT 'no'::character varying,
    org_id integer,
    feed_token_hash text,
    feed_token_created_at timestamp with time zone,
    feed_token text,
    CONSTRAINT approved_users_ai_working_group_check CHECK (((ai_working_group)::text = ANY ((ARRAY['yes'::character varying, 'no'::character varying])::text[]))),
    CONSTRAINT approved_users_user_role_check CHECK (((user_role)::text = ANY ((ARRAY['admin'::character varying, 'basic'::character varying, 'custom'::character varying])::text[])))
);


ALTER TABLE auth.approved_users OWNER TO legtracker;

--
-- Name: approved_users_approved_user_id_seq; Type: SEQUENCE; Schema: auth; Owner: legtracker
--

CREATE SEQUENCE auth.approved_users_approved_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE auth.approved_users_approved_user_id_seq OWNER TO legtracker;

--
-- Name: approved_users_approved_user_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: legtracker
--

ALTER SEQUENCE auth.approved_users_approved_user_id_seq OWNED BY auth.approved_users.approved_user_id;


--
-- Name: approved_users approved_user_id; Type: DEFAULT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_users ALTER COLUMN approved_user_id SET DEFAULT nextval('auth.approved_users_approved_user_id_seq'::regclass);


--
-- Name: approved_users approved_users_email_key; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_users
    ADD CONSTRAINT approved_users_email_key UNIQUE (email);


--
-- Name: approved_users approved_users_feed_token_hash_key; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_users
    ADD CONSTRAINT approved_users_feed_token_hash_key UNIQUE (feed_token_hash);


--
-- Name: approved_users approved_users_pkey; Type: CONSTRAINT; Schema: auth; Owner: legtracker
--

ALTER TABLE ONLY auth.approved_users
    ADD CONSTRAINT approved_users_pkey PRIMARY KEY (approved_user_id);


--
-- Name: idx_approved_users_feed_token; Type: INDEX; Schema: auth; Owner: legtracker
--

CREATE INDEX idx_approved_users_feed_token ON auth.approved_users USING btree (feed_token_hash) WHERE (feed_token_hash IS NOT NULL);


--
-- Name: TABLE approved_users; Type: ACL; Schema: auth; Owner: legtracker
--

REVOKE SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_users FROM legtracker;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_users TO legtracker WITH GRANT OPTION;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE auth.approved_users TO kschiedeck;


--
-- Name: SEQUENCE approved_users_approved_user_id_seq; Type: ACL; Schema: auth; Owner: legtracker
--

GRANT ALL ON SEQUENCE auth.approved_users_approved_user_id_seq TO kschiedeck;


--
-- PostgreSQL database dump complete
--

\unrestrict uxY735DlXQfn3MlUAkh1TZHR1ewhYn1HWcBtv8SsIh1LJTtF77Y1rB5nO5Euw4c

