--
-- PostgreSQL database dump
--

\restrict G1y3b6wRsIW4F7fbnH4CugHjJA88tkuxdfydFKl0OxHwvaxl3FIguOFC3ho9Ee7

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
-- Name: bill_topics; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.bill_topics (
    openstates_bill_id text,
    topic_phrase text,
    match_method text NOT NULL,
    similarity double precision,
    assigned_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT bill_topics_match_method_check CHECK ((match_method = ANY (ARRAY['keyword'::text, 'similarity'::text])))
);


ALTER TABLE snapshot.bill_topics OWNER TO legtracker;

--
-- Name: bill_topics_assigned_at_idx; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX bill_topics_assigned_at_idx ON snapshot.bill_topics USING btree (assigned_at);


--
-- Name: bill_topics bill_topics_openstates_bill_id_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.bill_topics
    ADD CONSTRAINT bill_topics_openstates_bill_id_fkey FOREIGN KEY (openstates_bill_id) REFERENCES snapshot.bill(openstates_bill_id) ON DELETE CASCADE;


--
-- Name: bill_topics bill_topics_topic_phrase_fkey; Type: FK CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.bill_topics
    ADD CONSTRAINT bill_topics_topic_phrase_fkey FOREIGN KEY (topic_phrase) REFERENCES snapshot.topic_embedding(topic_phrase);


--
-- PostgreSQL database dump complete
--

\unrestrict G1y3b6wRsIW4F7fbnH4CugHjJA88tkuxdfydFKl0OxHwvaxl3FIguOFC3ho9Ee7

