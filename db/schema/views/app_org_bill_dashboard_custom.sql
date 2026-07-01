--
-- PostgreSQL database dump
--

\restrict FBE36lVLJBgOQJOv1OLcbO7db9jtrudiSo9gJnCU2ecCaZA3FggHZ6uyuKB7JVI

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
-- Name: org_bill_dashboard_custom; Type: VIEW; Schema: app; Owner: legtracker
--

CREATE VIEW app.org_bill_dashboard_custom AS
 SELECT b.openstates_bill_id,
    b.bill_number,
    b.bill_name,
    b.status,
    b.date_introduced,
    b.leg_session,
    b.author,
    b.coauthors,
    b.chamber,
    b.leginfo_link,
    b.bill_text,
    b.bill_history,
    b.bill_event,
    b.event_text,
    b.assigned_topics,
    b.last_updated_on,
    obd.org_id,
    bcd.org_position,
    bcd.assigned_to,
    bcd.last_updated_on AS changed_on
   FROM ((app.bills_mv b
     JOIN app.org_bill_dashboard obd ON ((obd.openstates_bill_id = b.openstates_bill_id)))
     LEFT JOIN app.bill_custom_details bcd ON (((bcd.openstates_bill_id = b.openstates_bill_id) AND (bcd.last_updated_org_id = obd.org_id))));


ALTER VIEW app.org_bill_dashboard_custom OWNER TO legtracker;

--
-- PostgreSQL database dump complete
--

\unrestrict FBE36lVLJBgOQJOv1OLcbO7db9jtrudiSo9gJnCU2ecCaZA3FggHZ6uyuKB7JVI

