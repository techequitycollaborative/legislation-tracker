--
-- PostgreSQL database dump
--

\restrict vYArL3bUG0PJBXsEIGVy61S4NL274qTjjw64bYdcloilNOgWnIWTgf0rbWTBipL

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
-- Name: people_roles; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people_roles (
    openstates_people_id text NOT NULL,
    org_classification text,
    district integer
);


ALTER TABLE snapshot.people_roles OWNER TO legtracker;

--
-- Name: people_roles people_roles_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people_roles
    ADD CONSTRAINT people_roles_pkey PRIMARY KEY (openstates_people_id);


--
-- PostgreSQL database dump complete
--

\unrestrict vYArL3bUG0PJBXsEIGVy61S4NL274qTjjw64bYdcloilNOgWnIWTgf0rbWTBipL

