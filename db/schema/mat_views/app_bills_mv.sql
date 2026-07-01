--
-- PostgreSQL database dump
--

\restrict X3F3Qd20kjazT4E0RI9njwQfmiqR1fRwbPdOGaBn3efGXHh9cgSea4uidRuyrBH

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
-- Name: bills_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.bills_mv AS
 WITH temp_bills AS (
         SELECT bill.openstates_bill_id,
            (("left"(bill.session, 4) || '-'::text) || "right"(bill.session, 4)) AS leg_session,
            bill.chamber,
            bill.bill_num AS bill_number,
            bill.title AS bill_name,
            (bill.first_action_date)::date AS date_introduced,
            (bill.last_action_date)::date AS last_updated_on,
            bill.abstract AS bill_text,
            concat('https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=', replace(bill.session, '-'::text, ''::text), '0', replace(bill.bill_num, ' '::text, ''::text)) AS leginfo_link
           FROM snapshot.bill
          WHERE (((("left"(bill.session, 4) || '-'::text) || "right"(bill.session, 4)) = '2025-2026'::text) AND (bill.bill_num !~~ 'ACR%'::text) AND (bill.bill_num !~~ 'HR%'::text) AND (bill.bill_num !~~ 'SCR%'::text) AND (bill.bill_num !~~ 'SR%'::text) AND (bill.bill_num !~~ 'SJR%'::text) AND (bill.bill_num !~~ 'AJR%'::text) AND ((bill.last_action_date >= '2025-12-01'::text) OR (bill.openstates_bill_id IN ( SELECT DISTINCT bill_history.openstates_bill_id
                   FROM app.bill_history
                  WHERE (lower(bill_history.description) ~~ '%inactive file%'::text))) OR (bill.bill_num = 'AB 412'::text) OR (bill.bill_num = 'SB 435'::text) OR (bill.bill_num = 'AB 882'::text)))
        ), latest_status AS (
         SELECT DISTINCT ON (bill_history.openstates_bill_id) bill_history.openstates_bill_id,
            bill_history.description AS status
           FROM app.bill_history
          ORDER BY bill_history.openstates_bill_id, (bill_history.action_order)::integer DESC
        ), full_history AS (
         SELECT bill_history.openstates_bill_id,
            string_agg(((bill_history.action_date || ' >> '::text) || bill_history.description), ', '::text ORDER BY bill_history.action_date) AS bill_history
           FROM app.bill_history
          GROUP BY bill_history.openstates_bill_id
        ), bill_authors AS (
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
        ), bill_hearings AS (
         SELECT DISTINCT ON (hb.openstates_bill_id) hb.id,
            hb.hearing_id,
            hb.openstates_bill_id,
            hb.file_order,
            h_1.date AS hearing_date,
            h_1.name AS hearing_name
           FROM (snapshot.hearing_bills hb
             JOIN snapshot.hearings h_1 ON ((hb.hearing_id = h_1.hearing_id)))
          WHERE (h_1.date >= CURRENT_DATE)
          ORDER BY hb.openstates_bill_id, h_1.date
        ), bill_topics AS (
         SELECT bt.openstates_bill_id,
            string_agg(bt.topic_phrase, '; '::text ORDER BY bt.topic_phrase) AS assigned_topics
           FROM ( SELECT DISTINCT bill_topics.openstates_bill_id,
                    bill_topics.topic_phrase
                   FROM snapshot.bill_topics) bt
          GROUP BY bt.openstates_bill_id
        )
 SELECT b.openstates_bill_id,
    b.bill_number,
    b.bill_name,
    s.status,
    b.date_introduced,
    b.leg_session,
    a.author,
    a.coauthors,
    b.chamber,
    b.leginfo_link,
    b.bill_text,
    h.bill_history,
    bh.hearing_date AS bill_event,
    bh.hearing_name AS event_text,
    t.assigned_topics,
    b.last_updated_on
   FROM (((((temp_bills b
     LEFT JOIN latest_status s ON ((b.openstates_bill_id = s.openstates_bill_id)))
     LEFT JOIN full_history h ON ((b.openstates_bill_id = h.openstates_bill_id)))
     LEFT JOIN bill_authors a ON ((b.openstates_bill_id = a.openstates_bill_id)))
     LEFT JOIN bill_hearings bh ON ((b.openstates_bill_id = (bh.openstates_bill_id)::text)))
     LEFT JOIN bill_topics t ON ((b.openstates_bill_id = t.openstates_bill_id)))
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.bills_mv OWNER TO legtracker;

--
-- Name: idx_bills_mv_pk; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX idx_bills_mv_pk ON app.bills_mv USING btree (openstates_bill_id);


--
-- PostgreSQL database dump complete
--

\unrestrict X3F3Qd20kjazT4E0RI9njwQfmiqR1fRwbPdOGaBn3efGXHh9cgSea4uidRuyrBH

