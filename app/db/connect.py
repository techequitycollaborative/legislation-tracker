import psycopg2
from psycopg2 import pool, OperationalError
from db.config import db_config as config

############################# GLOBAL VARIABLES #################################
_pool = None  # module-level singleton

############################# CONNECTION POOLING ###############################

def get_pool():
    # use global variable
    global _pool

    # Only import package when _pool hasn't ben assigned (at session start)
    if _pool is None:
        # Import streamlit lazily inside to avoid triggering runtime before set_page_config
        from streamlit.runtime.caching import cache_resource
    
    # Create a connection pool and cache the resource
    @cache_resource
    def _make_pool():
        return pool.SimpleConnectionPool(minconn=5, maxconn=50, **config('postgres'))
    
    # Call the cached connection pool
    pg_pool = _make_pool()

    # Verify at least one connection is valid
    try:
        conn = pg_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        pg_pool.putconn(conn)
    except OperationalError:
        # Connection is stale - we need to rebuild pool
        # (Clears Streamlit cache and re-create resource)
        cache_resource.clear()
        pg_pool = _make_pool()

    # Return the cached connection pool
    return _make_pool()

################################ DEPRECATED ###################################
def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
