--
-- PostgreSQL database dump
--

\restrict mC7TN8b5of9I9NwAv4ZXyjmaX3qDEMd2MYbYb0C02pN62qsVC0zsqoRBLn5xwJh

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
-- Name: legislators; Type: VIEW; Schema: app; Owner: legtracker
--

CREATE VIEW app.legislators AS
 WITH temp_people AS (
         SELECT people.openstates_people_id,
            people.name,
            people.party,
            people.updated_at
           FROM snapshot.people
        ), temp_roles AS (
         SELECT DISTINCT ON (people_roles.openstates_people_id) people_roles.openstates_people_id,
            people_roles.district,
                CASE
                    WHEN (people_roles.org_classification = 'lower'::text) THEN 'Assembly'::text
                    ELSE 'Senate'::text
                END AS chamber
           FROM snapshot.people_roles
        ), temp_names AS (
         SELECT people_names.openstates_people_id,
            string_agg(people_names.alt_name, '; '::text ORDER BY people_names.alt_name) AS other_names
           FROM snapshot.people_names
          GROUP BY people_names.openstates_people_id
        ), temp_sources AS (
         SELECT people_sources.openstates_people_id,
            string_agg(people_sources.source_url, '\n'::text) AS ext_sources
           FROM snapshot.people_sources
          GROUP BY people_sources.openstates_people_id
        ), temp_offices AS (
         SELECT people_offices.openstates_people_id,
            string_agg((((((
                CASE
                    WHEN (people_offices.classification = 'capitol'::text) THEN people_offices.name
                    ELSE split_part(people_offices.address, ', '::text, '-2'::integer)
                END || '@@'::text) || 'Phone: '::text) || people_offices.phone) || '@@'::text) || people_offices.address), '\n'::text) AS office_details
           FROM snapshot.people_offices
          GROUP BY people_offices.openstates_people_id
        ), temp_contacts AS (
         SELECT people_contacts.openstates_people_id,
            string_agg(((((((((people_contacts.people_contact_id || '@@'::text) || people_contacts.issue_area) || '@@'::text) || people_contacts.staffer_type) || '@@'::text) || people_contacts.staffer_contact) || '@@'::text) || people_contacts.generated_email), '\n'::text) AS issue_contacts
           FROM snapshot.people_contacts
          GROUP BY people_contacts.openstates_people_id
        )
 SELECT p.openstates_people_id,
    (p.updated_at)::date AS last_updated_on,
    p.name,
    p.party,
    r.chamber,
    r.district,
    n.other_names,
    s.ext_sources,
    o.office_details,
    c.issue_contacts
   FROM (((((temp_people p
     LEFT JOIN temp_roles r ON ((p.openstates_people_id = r.openstates_people_id)))
     LEFT JOIN temp_names n ON ((p.openstates_people_id = n.openstates_people_id)))
     LEFT JOIN temp_sources s ON ((p.openstates_people_id = s.openstates_people_id)))
     LEFT JOIN temp_offices o ON ((p.openstates_people_id = o.openstates_people_id)))
     LEFT JOIN temp_contacts c ON ((p.openstates_people_id = c.openstates_people_id)));


ALTER VIEW app.legislators OWNER TO legtracker;

--
-- PostgreSQL database dump complete
--

\unrestrict mC7TN8b5of9I9NwAv4ZXyjmaX3qDEMd2MYbYb0C02pN62qsVC0zsqoRBLn5xwJh

