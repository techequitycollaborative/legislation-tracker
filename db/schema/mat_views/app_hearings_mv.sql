--
-- PostgreSQL database dump
--

\restrict 8a9iDbjv61yOo7ReLaDYTf2Ku0vOhdBZzBgXDcDG6XrUwpHL7BLNLC9pZOclBoP

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
-- Name: hearings_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.hearings_mv AS
 SELECT h.hearing_id,
    h.date AS hearing_date,
    h.name AS hearing_name,
    h.time_verbatim AS hearing_time_verbatim,
    h.time_normalized AS hearing_time,
    h.is_allday,
    h.location AS hearing_location,
    h.room AS hearing_room,
    h.chamber_id,
    h.committee_id,
    h.canceled_at,
    h.created_at,
    h.updated_at
   FROM snapshot.hearings h
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.hearings_mv OWNER TO legtracker;

--
-- Name: idx_hearings_chamber; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearings_chamber ON app.hearings_mv USING btree (chamber_id);


--
-- Name: idx_hearings_date; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearings_date ON app.hearings_mv USING btree (hearing_date);


--
-- Name: idx_hearings_pk; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX idx_hearings_pk ON app.hearings_mv USING btree (hearing_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 8a9iDbjv61yOo7ReLaDYTf2Ku0vOhdBZzBgXDcDG6XrUwpHL7BLNLC9pZOclBoP

