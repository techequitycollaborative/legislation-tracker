--
-- PostgreSQL database dump
--

\restrict aTIQ1jCUobqOURKgFNQ93DwJkK8asWpoKnPpoW5RfeiYOWWCg6Fv9R16IJYPRxj

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
-- Name: bill_embedding; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.bill_embedding (
    openstates_bill_id text NOT NULL,
    weighted_embedding public.vector(384),
    computed_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE snapshot.bill_embedding OWNER TO legtracker;

--
-- Name: bill_embedding bill_embedding_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.bill_embedding
    ADD CONSTRAINT bill_embedding_pkey PRIMARY KEY (openstates_bill_id);


--
-- Name: bill_embedding_computed_at_idx; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX bill_embedding_computed_at_idx ON snapshot.bill_embedding USING btree (computed_at);


--
-- Name: bill_embedding bill_embedding_openstates_bill_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.bill_embedding
    ADD CONSTRAINT bill_embedding_openstates_bill_id_fkey FOREIGN KEY (openstates_bill_id) REFERENCES snapshot.bill(openstates_bill_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict aTIQ1jCUobqOURKgFNQ93DwJkK8asWpoKnPpoW5RfeiYOWWCg6Fv9R16IJYPRxj

