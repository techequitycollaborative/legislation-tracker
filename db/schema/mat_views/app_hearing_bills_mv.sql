--
-- PostgreSQL database dump
--

\restrict RcfQxcnyd5qUPyfadUa5Aqv8hgqWzZEzCL236I4t7u80y4zRboWJvm9lbeqQ1mj

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
-- Name: hearing_bills_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.hearing_bills_mv AS
 WITH bill_authors AS (
         SELECT bill_sponsor.openstates_bill_id,
            COALESCE(max(
                CASE
                    WHEN (bill_sponsor.primary_author = 'True'::text) THEN bill_sponsor.full_name
                    ELSE NULL::text
                END), max(
                CASE
                    WHEN (((bill_sponsor.primary_author IS NULL) OR (bill_sponsor.primary_author = ''::text)) AND (bill_sponsor.title = 'author'::text)) THEN bill_sponsor.name
                    ELSE NULL::text
                END)) AS author,
            COALESCE(string_agg(
                CASE
                    WHEN (bill_sponsor.primary_author = 'False'::text) THEN bill_sponsor.full_name
                    ELSE NULL::text
                END, ', '::text), string_agg(
                CASE
                    WHEN (((bill_sponsor.primary_author IS NULL) OR (bill_sponsor.primary_author = ''::text)) AND (bill_sponsor.title <> 'author'::text)) THEN bill_sponsor.name
                    ELSE NULL::text
                END, ', '::text)) AS coauthors
           FROM snapshot.bill_sponsor
          GROUP BY bill_sponsor.openstates_bill_id
        )
 SELECT hb.hearing_id,
    hb.openstates_bill_id,
    hb.file_order,
    hb.footnote,
    hb.footnote_symbol,
    b.bill_num AS bill_number,
    b.title AS bill_name,
    b.first_action_date AS date_introduced,
    a.author AS bill_author,
    concat('https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=', replace(b.session, '-'::text, ''::text), '0', replace(b.bill_num, ' '::text, ''::text)) AS leginfo_link
   FROM ((snapshot.hearing_bills hb
     LEFT JOIN snapshot.bill b ON ((b.openstates_bill_id = (hb.openstates_bill_id)::text)))
     LEFT JOIN bill_authors a ON ((a.openstates_bill_id = (hb.openstates_bill_id)::text)))
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.hearing_bills_mv OWNER TO legtracker;

--
-- Name: idx_hearing_bills_bill; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearing_bills_bill ON app.hearing_bills_mv USING btree (openstates_bill_id);


--
-- Name: idx_hearing_bills_hearing; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE INDEX idx_hearing_bills_hearing ON app.hearing_bills_mv USING btree (hearing_id);


--
-- Name: idx_hearing_bills_pk; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX idx_hearing_bills_pk ON app.hearing_bills_mv USING btree (hearing_id, openstates_bill_id);


--
-- PostgreSQL database dump complete
--

\unrestrict RcfQxcnyd5qUPyfadUa5Aqv8hgqWzZEzCL236I4t7u80y4zRboWJvm9lbeqQ1mj

