import psycopg2
from psycopg2 import pool, OperationalError
from db.config import config

_pool = None  # module-level singleton

def get_pool():
    global _pool
    if _pool is None:
        # Import streamlit lazily inside to avoid triggering runtime before set_page_config
        from streamlit.runtime.caching import cache_resource
    def _make_pool():
        return pool.SimpleConnectionPool(minconn=1, maxconn=10, **config('postgres'))
    
    pg_pool = _make_pool()
    # Defensive: verify at least one connection is valid
    try:
        conn = pg_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        pg_pool.putconn(conn)
    except OperationalError:
        # Connection is stale → rebuild pool
        # (Clears Streamlit cache and re-create resource)
        st.cache_resource.clear()
        pg_pool = _make_pool()
    return _make_pool()

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
