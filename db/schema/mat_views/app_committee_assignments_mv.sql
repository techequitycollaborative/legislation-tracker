--
-- PostgreSQL database dump
--

\restrict CMmHQjOmAp65nhTyT4mbY8eHghJHPixp4vnuen8eN034zYTcb6anNaeWkXveHPo

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
-- Name: committee_assignments_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.committee_assignments_mv AS
 WITH temp_assign AS (
         SELECT committee_assignment.committee_assignment_id,
            committee_assignment.committee_id,
            committee_assignment.legislator_name,
            committee_assignment.assignment_type,
            (("left"((committee_assignment.session)::text, 4) || '-'::text) || "right"((committee_assignment.session)::text, 4)) AS leg_session
           FROM snapshot.committee_assignment
        ), temp_committee AS (
         SELECT committee.committee_id,
            committee.chamber_id,
            committee.name AS committee_name
           FROM snapshot.committee
        ), committee_name_assign AS (
         SELECT cm.committee_assignment_id,
            c.committee_name,
            c.committee_id,
            c.chamber_id,
            cm.legislator_name,
            cm.assignment_type,
            cm.leg_session
           FROM (temp_assign cm
             LEFT JOIN temp_committee c ON ((cm.committee_id = c.committee_id)))
        )
 SELECT committee_name_assign.committee_assignment_id,
    committee_name_assign.committee_name,
    committee_name_assign.committee_id,
    committee_name_assign.chamber_id,
    committee_name_assign.legislator_name,
    committee_name_assign.assignment_type,
    committee_name_assign.leg_session
   FROM committee_name_assign
  ORDER BY committee_name_assign.chamber_id, committee_name_assign.committee_name
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.committee_assignments_mv OWNER TO legtracker;

--
-- PostgreSQL database dump complete
--

\unrestrict CMmHQjOmAp65nhTyT4mbY8eHghJHPixp4vnuen8eN034zYTcb6anNaeWkXveHPo

