# db/connect.py
from contextlib import contextmanager
import time
import functools
import logging
import psycopg2
import psycopg2.extras
from db.config import config

logger = logging.getLogger(__name__)


def _connect():
    """Shared connection setup used by with_connection, get_conn, and get_cursor."""
    connect_start = time.time()
    conn = psycopg2.connect(**config("postgres"))
    connect_time = (time.time() - connect_start) * 1000
    logger.info(f"Connection established in {connect_time:.1f}ms")
    return conn


def with_connection():
    """
    Decorator for sharing a single database connection across multiple 
    function calls.

    Opens a connection and injects it as the `conn` keyword argument. The 
    connection is closed automatically when the decorated function returns. 
    This decorator does not perform any commits; transaction management 
    (commit/rollback) is left to the individual operations or the caller.

    Safe to nest: If a `conn` is already provided in the kwargs, it reuses 
    that connection instead of creating a new one.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.get("conn") is not None:
                return func(*args, **kwargs)  # already inside a connection scope

            conn = None
            start_time = time.time()
            try:
                conn = _connect()
                kwargs["conn"] = conn
                result = func(*args, **kwargs)
                total_time = (time.time() - start_time) * 1000
                logger.info(f"{func.__name__} completed (total: {total_time:.1f}ms)")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e!r}")
                if conn and not conn.closed:
                    try:
                        conn.rollback()
                    except psycopg2.InterfaceError:
                        logger.warning(f"{func.__name__}: connection already closed, skipping rollback")
                raise  # always re-raise the ORIGINAL exception, not a cleanup error
            finally:
                if conn and not conn.closed:
                    conn.close()
        return wrapper
    return decorator


@contextmanager
def get_conn():
    """
    Provides raw connection access for manual transaction management or 
    bulk operations.

    Yields a standard psycopg2 connection object. Does not perform any 
    automatic commits or rollbacks. The caller is responsible for calling 
    `conn.commit()` or `conn.rollback()` as needed. The connection is 
    automatically closed when the context manager exits.
    """
    conn = None
    start_time = time.time()
    try:
        conn = _connect()

        yield conn

    except Exception as e:
        logger.error(f"Transaction failed: {e!r}")
        if conn and not conn.closed:
            try:
                conn.rollback()
                logger.error("Transaction rolled back")
            except psycopg2.InterfaceError:
                logger.warning("get_conn: connection already closed, skipping rollback")
        raise
    finally:
        if conn and not conn.closed:
            conn.close()
            close_time = (time.time() - start_time) * 1000
            logger.info(f"Database connection closed in {close_time:.1f}ms")


@contextmanager
def get_cursor(conn=None):
    """
    Yields a RealDictCursor for a single statement.

    If `conn` is None, opens a new connection and closes it on exit. 
    If `conn` is provided, reuses the existing connection. 

    This function does NOT perform automatic commits after execution. 
    Callers must explicitly commit the transaction on the connection 
    object if persistence is required. This allows for multi-statement 
    transactions to be managed manually by the caller.
    """
    owns_conn = conn is None
    try:
        if owns_conn:
            conn = _connect()

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur

    except Exception as e:
        logger.error(f"get_cursor failed: {e!r}")
        if conn and not conn.closed:
            try:
                conn.rollback()
            except psycopg2.InterfaceError:
                logger.warning("get_cursor: connection already closed, skipping rollback")
        raise
    finally:
        if owns_conn and conn and not conn.closed:
            conn.close()


def fetch_all(query, params=(), as_dataframe=False, conn=None):
    """
    Run a SELECT and return all rows.

    as_dataframe=True returns a pandas DataFrame instead of a list of dicts
    (pandas is imported lazily -- callers that never ask for a dataframe,
    e.g. Flask/pipeline, don't pay the import cost).

    conn: optional shared connection (see get_cursor). Omit for a standalone
    call; pass through when calling from inside a with_connection-decorated
    function.
    """
    with get_cursor(conn=conn) as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
    if as_dataframe:
        import pandas as pd  # lazy import
        return pd.DataFrame(rows)
    return rows


def fetch_one(query, params=(), conn=None):
    """Run a SELECT and return a single row (dict) or None if no match."""
    with get_cursor(conn=conn) as cur:
        cur.execute(query, params)
        return cur.fetchone()


def execute(query, params=(), conn=None) -> int:
    """
    Run a single-statement INSERT/UPDATE/DELETE. Returns affected row count.
    Commits automatically (see get_cursor) whether or not conn is shared.
    """
    with get_cursor(conn=conn) as cur:
        cur.execute(query, params)
        return cur.rowcount