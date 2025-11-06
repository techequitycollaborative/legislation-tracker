import psycopg2
from psycopg2.pool import SimpleConnectionPool
from db.config import config

pool = SimpleConnectionPool(minconn=1, maxconn=10, **config('postgres'))

def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
