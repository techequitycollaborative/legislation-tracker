from contextlib import contextmanager
import psycopg2
from db.config import db_config as config

@contextmanager
def get_connection():
    """
    Context manager for database connections through PgBouncer.
    Automatically handles connection cleanup.
    
    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM table")
                data = cur.fetchall()
    """
    conn = None
    try:
        conn = psycopg2.connect(**config('postgres'))
        yield conn
    finally:
        if conn is not None:
            conn.close()  # Returns connection to PgBouncer pool
            print("Database connection closed.")