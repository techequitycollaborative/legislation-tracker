--
-- PostgreSQL database dump
--

\restrict wGLiW6uHcyBjcaTTRkgeNFuyvpKsfud1x3cHUpmYxU5ZWvmOxL2C7NeQjUBnyr2

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
-- Name: topic_embedding; Type: TABLE; Schema: snapshot; Owner: legtracker
--

CREATE TABLE snapshot.topic_embedding (
    topic_id integer NOT NULL,
    topic_phrase text NOT NULL,
    keywords text[],
    embedding public.vector(384),
    embedding_updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE snapshot.topic_embedding OWNER TO legtracker;

--
-- Name: topic_embedding_topic_id_seq; Type: SEQUENCE; Schema: snapshot; Owner: legtracker
--

CREATE SEQUENCE snapshot.topic_embedding_topic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE snapshot.topic_embedding_topic_id_seq OWNER TO legtracker;

--
-- Name: topic_embedding_topic_id_seq; Type: SEQUENCE OWNED BY; Schema: snapshot; Owner: legtracker
--

ALTER SEQUENCE snapshot.topic_embedding_topic_id_seq OWNED BY snapshot.topic_embedding.topic_id;


--
-- Name: topic_embedding topic_id; Type: DEFAULT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.topic_embedding ALTER COLUMN topic_id SET DEFAULT nextval('snapshot.topic_embedding_topic_id_seq'::regclass);


--
-- Name: topic_embedding topic_embedding_pkey; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.topic_embedding
    ADD CONSTRAINT topic_embedding_pkey PRIMARY KEY (topic_id);


--
-- Name: topic_embedding topic_embedding_topic_phrase_key; Type: CONSTRAINT; Schema: snapshot; Owner: legtracker
--

ALTER TABLE ONLY snapshot.topic_embedding
    ADD CONSTRAINT topic_embedding_topic_phrase_key UNIQUE (topic_phrase);


--
-- Name: topic_embedding_embedding_updated_at_idx; Type: INDEX; Schema: snapshot; Owner: legtracker
--

CREATE INDEX topic_embedding_embedding_updated_at_idx ON snapshot.topic_embedding USING btree (embedding_updated_at);


--
-- PostgreSQL database dump complete
--

\unrestrict wGLiW6uHcyBjcaTTRkgeNFuyvpKsfud1x3cHUpmYxU5ZWvmOxL2C7NeQjUBnyr2

