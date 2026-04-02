from contextlib import contextmanager
import psycopg2
from db.config import config
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_conn():
    conn = None
    try:
        params = config("postgres")
        conn = psycopg2.connect(**params)
        yield conn
        conn.commit()
        logger.info("Transaction committed")
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
            conn.close()
            logger.info("Database connection closed")
