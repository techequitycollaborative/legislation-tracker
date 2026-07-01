--
-- PostgreSQL database dump
--

\restrict NPgq3Nw5bFQwQQPDZ2nEnNLMbz02K8Pnrb833zBQcsvobsECatfgIrsEenyNkhf

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

--
-- Name: bill_history; Type: VIEW; Schema: app; Owner: legtracker
--

CREATE VIEW app.bill_history AS
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
 SELECT filtered_action.openstates_bill_id,
    filtered_action.bill_num,
    filtered_action.leg_session,
    filtered_action.action_date,
    filtered_action.description,
    filtered_action.action_order,
    filtered_action.first_action_order
   FROM filtered_action
  ORDER BY filtered_action.openstates_bill_id, filtered_action.action_order;


ALTER VIEW app.bill_history OWNER TO legtracker;

--
-- PostgreSQL database dump complete
--

\unrestrict NPgq3Nw5bFQwQQPDZ2nEnNLMbz02K8Pnrb833zBQcsvobsECatfgIrsEenyNkhf

