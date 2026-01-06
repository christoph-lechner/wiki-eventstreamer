import psycopg
import os

def get_db_conn():
    conn = psycopg.connect(dbname   = os.environ['DB_DBNAME'],
                           user     = os.environ['DB_USER'], 
                           host     = os.environ['DB_HOST'],
                           password = os.environ['DB_PASSWORD'],
                           port     = os.environ['DB_PORT'],
                           sslmode='verify-full', sslrootcert='./isrgrootx1.pem')
    return conn
