# db/connect.py
from contextlib import contextmanager
import time
import logging
import psycopg2
import psycopg2.extras
from db.config import config

logger = logging.getLogger(__name__)


def _connect():
    """Shared connection setup used by both get_cursor and get_conn."""
    connect_start = time.time()
    conn = psycopg2.connect(**config("postgres"))
    connect_time = (time.time() - connect_start) * 1000
    logger.info(f"Connection established in {connect_time:.1f}ms")
    return conn


@contextmanager
def get_cursor(commit: bool = False):
    """
    Yields a RealDictCursor against a fresh connection, with timing/logging
    for connect, commit (if applicable), and close. Connection is opened and
    closed per call by design -- DO's managed pool (port 25061, transaction
    mode) handles pooling upstream, so we don't hold connections open here.

    Use this (or the fetch_all/fetch_one/execute helpers below) for standard
    single-statement queries. For bulk loads (copy_expert/execute_values) or
    multi-statement transactions, use get_conn() instead.
    """
    conn = None
    start_time = time.time()
    try:
        conn = _connect()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur

        if commit:
            commit_start = time.time()
            conn.commit()
            commit_time = (time.time() - commit_start) * 1000
            logger.info(f"Transaction committed in {commit_time:.1f}ms")

        total_time = (time.time() - start_time) * 1000
        logger.info(f"Query completed (total: {total_time:.1f}ms)")

    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e.pgerror}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Transaction rolled back: {str(e)}")
        raise
    finally:
        if conn:
            close_start = time.time()
            conn.close()
            close_time = (time.time() - close_start) * 1000
            logger.info(f"Database connection closed in {close_time:.1f}ms")


@contextmanager
def get_conn():
    """
    Raw connection access for bulk loads (copy_expert / execute_values) or
    multi-statement transactions that need to commit/rollback as one unit.
    Prefer get_cursor() / fetch_all() / fetch_one() / execute() for standard
    single-statement queries -- reach for this only when a call site needs
    more than one execute() to complete a logical operation, or needs
    cursor-level APIs like copy_expert.
    """
    conn = None
    start_time = time.time()
    try:
        conn = _connect()

        yield conn

        commit_start = time.time()
        conn.commit()
        commit_time = (time.time() - commit_start) * 1000

        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Transaction committed in {commit_time:.1f}ms (total: {total_time:.1f}ms)"
        )
    except psycopg2.DatabaseError as e:
        if conn:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e.pgerror}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Transaction rolled back: {str(e)}")
        raise
    finally:
        if conn:
            close_start = time.time()
            conn.close()
            close_time = (time.time() - close_start) * 1000
            logger.info(f"Database connection closed in {close_time:.1f}ms")


def fetch_all(query: str, params: tuple = (), as_dataframe: bool = False):
    with get_cursor() as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    if as_dataframe:
        import pandas as pd  # lazy import -- Flask/pipeline callers never pay for this
        return pd.DataFrame(rows)
    return rows


def fetch_one(query: str, params: tuple = ()):
    with get_cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()


def execute(query: str, params: tuple = ()) -> int:
    """For single-statement INSERT/UPDATE/DELETE. Returns affected row count."""
    with get_cursor(commit=True) as cur:
        cur.execute(query, params)
        return cur.rowcount