from contextlib import contextmanager
import psycopg2
import time
from db.config import config
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = None
    start_time = time.time()
    try:
        params = config("postgres")

        connect_start = time.time()
        conn = psycopg2.connect(**params)
        connect_time = (time.time() - connect_start) * 1000

        logger.info(f"Connection established in {connect_time:.1f}ms")

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
