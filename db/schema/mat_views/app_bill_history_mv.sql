--
-- PostgreSQL database dump
--

\restrict 5xSbDZkhXiBVZxp52GjaCJc8TqF8kk05KiUJeSghVoMpHqcZyimfi2OkXJcRS4A

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
-- Name: bill_history_mv; Type: MATERIALIZED VIEW; Schema: app; Owner: legtracker
--

CREATE MATERIALIZED VIEW app.bill_history_mv AS
 WITH temp_action AS (
         SELECT bill_action.openstates_bill_id,
            bill_action.chamber,
            bill_action.description,
            bill_action.action_date,
            bill_action.action_order
           FROM snapshot.bill_action
        ), temp_bills AS (
         SELECT bill.openstates_bill_id,
            bill.bill_num,
            bill.session
           FROM snapshot.bill
          WHERE ("left"(bill.session, 4) = '2025'::text)
        ), combined_table AS (
         SELECT b.openstates_bill_id,
            b.bill_num,
            (("left"(b.session, 4) || '-'::text) || "right"(b.session, 4)) AS leg_session,
            a.action_date,
            a.description,
            a.action_order
           FROM (temp_bills b
             LEFT JOIN temp_action a ON ((b.openstates_bill_id = a.openstates_bill_id)))
        ), partition_action AS (
         SELECT combined_table.openstates_bill_id,
            combined_table.bill_num,
            combined_table.leg_session,
            combined_table.action_date,
            combined_table.description,
            combined_table.action_order,
            first_value(combined_table.action_order) OVER (PARTITION BY combined_table.openstates_bill_id, combined_table.bill_num ORDER BY combined_table.action_order) AS first_action_order
           FROM combined_table
        ), filtered_action AS (
         SELECT partition_action.openstates_bill_id,
            partition_action.bill_num,
            partition_action.leg_session,
            partition_action.action_date,
            partition_action.description,
            partition_action.action_order,
            partition_action.first_action_order
           FROM partition_action
          WHERE (partition_action.action_date >= '2024-12-02'::text)
        )
 SELECT row_number() OVER (ORDER BY filtered_action.openstates_bill_id, filtered_action.action_order, filtered_action.action_date) AS row_id,
    filtered_action.openstates_bill_id,
    filtered_action.bill_num,
    filtered_action.leg_session,
    filtered_action.action_date,
    filtered_action.description,
    filtered_action.action_order,
    filtered_action.first_action_order
   FROM filtered_action
  ORDER BY filtered_action.openstates_bill_id, filtered_action.action_order
  WITH NO DATA;


ALTER MATERIALIZED VIEW app.bill_history_mv OWNER TO legtracker;

--
-- Name: idx_bill_history_mv_pk; Type: INDEX; Schema: app; Owner: legtracker
--

CREATE UNIQUE INDEX idx_bill_history_mv_pk ON app.bill_history_mv USING btree (row_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 5xSbDZkhXiBVZxp52GjaCJc8TqF8kk05KiUJeSghVoMpHqcZyimfi2OkXJcRS4A

