--
-- PostgreSQL database dump
--

\restrict LYyCpgTnap77bwpN31P2S8oDdFYwaiW92u1C6l6NA2TrEWpAw3UiwWret6XRaz8

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
-- Name: hearing_deadlines_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.hearing_deadlines_mv AS
 SELECT hd.id,
    hd.hearing_id,
    hd.deadline_date,
    hd.deadline_type,
    h.date AS hearing_date,
    h.name AS hearing_name,
    h.chamber_id,
    h.committee_id
   FROM (snapshot.hearing_deadlines hd
     JOIN snapshot.hearings h ON ((h.hearing_id = hd.hearing_id)))
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.hearing_deadlines_mv OWNER TO legtracker;

--
-- Name: idx_hearing_deadlines_date; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearing_deadlines_date ON app.hearing_deadlines_mv USING btree (deadline_date);


--
-- Name: idx_hearing_deadlines_hearing; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearing_deadlines_hearing ON app.hearing_deadlines_mv USING btree (hearing_id);


--
-- Name: idx_hearing_deadlines_pk; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX idx_hearing_deadlines_pk ON app.hearing_deadlines_mv USING btree (id);


--
-- PostgreSQL database dump complete
--

\unrestrict LYyCpgTnap77bwpN31P2S8oDdFYwaiW92u1C6l6NA2TrEWpAw3UiwWret6XRaz8

