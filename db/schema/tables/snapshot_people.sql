--
-- PostgreSQL database dump
--

\restrict vxnREtlaexS45LNR1HWQgqnxAwL54uBixNHEm5hldtgO7TykeIrUZ3cwHEfKOg1

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
-- Name: people; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.people (
    openstates_people_id text NOT NULL,
    name text,
    party text,
    updated_at text
);


ALTER TABLE snapshot.people OWNER TO legtracker;

--
-- Name: people people_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (openstates_people_id);


--
-- PostgreSQL database dump complete
--

\unrestrict vxnREtlaexS45LNR1HWQgqnxAwL54uBixNHEm5hldtgO7TykeIrUZ3cwHEfKOg1

