--
-- PostgreSQL database dump
--

\restrict syVyGBi1NIqREjlCwEDXNzOqyyrdKTk8dalKVaMJ0YnukReeXZPHjaTCscM2ZcE

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
-- Name: committees_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.committees_mv AS
 WITH temp_committee AS (
         SELECT committee.committee_id,
            committee.chamber_id,
            committee.name AS committee_name,
            committee.webpage_link
           FROM snapshot.committee
        ), upcoming_schedule AS (
         SELECT DISTINCT ON (c_1.committee_id) c_1.committee_id,
            bs.chamber_id,
            bs.event_date,
            bs.event_text
           FROM (snapshot.bill_schedule bs
             JOIN temp_committee c_1 ON (((lower(bs.event_text) ~~ lower(concat('%', c_1.committee_name, '%'))) AND (c_1.chamber_id = bs.chamber_id))))
          WHERE (bs.event_date >= CURRENT_DATE)
          ORDER BY c_1.committee_id, bs.event_date
        ), full_membership AS (
         SELECT committee_assignments_mv.committee_id,
            max((
                CASE
                    WHEN ((committee_assignments_mv.assignment_type)::text = 'Chair'::text) THEN committee_assignments_mv.legislator_name
                    ELSE NULL::character varying
                END)::text) AS committee_chair,
            max((
                CASE
                    WHEN ((committee_assignments_mv.assignment_type)::text = 'Vice Chair'::text) THEN committee_assignments_mv.legislator_name
                    ELSE NULL::character varying
                END)::text) AS committee_vice_chair,
            string_agg((
                CASE
                    WHEN ((committee_assignments_mv.assignment_type)::text = 'Member'::text) THEN committee_assignments_mv.legislator_name
                    ELSE NULL::character varying
                END)::text, '; '::text) AS committee_members,
            count(
                CASE
                    WHEN ((committee_assignments_mv.assignment_type)::text = 'Member'::text) THEN 1
                    ELSE NULL::integer
                END) AS member_count,
            count(
                CASE
                    WHEN ((committee_assignments_mv.assignment_type)::text = ANY ((ARRAY['Member'::character varying, 'Chair'::character varying, 'Vice Chair'::character varying])::text[])) THEN 1
                    ELSE NULL::integer
                END) AS total_members
           FROM app.committee_assignments_mv
          GROUP BY committee_assignments_mv.committee_id
        )
 SELECT c.committee_id,
    c.chamber_id,
    c.committee_name,
    c.webpage_link,
    us.event_date AS committee_event,
    fm.committee_chair,
    fm.committee_vice_chair,
    fm.committee_members,
    fm.member_count,
    fm.total_members
   FROM ((temp_committee c
     LEFT JOIN upcoming_schedule us ON ((c.committee_id = us.committee_id)))
     LEFT JOIN full_membership fm ON ((c.committee_id = fm.committee_id)))
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.committees_mv OWNER TO legtracker;

--
-- Name: committees_mv_committee_id_idx; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX committees_mv_committee_id_idx ON app.committees_mv USING btree (committee_id);


--
-- PostgreSQL database dump complete
--

\unrestrict syVyGBi1NIqREjlCwEDXNzOqyyrdKTk8dalKVaMJ0YnukReeXZPHjaTCscM2ZcE

