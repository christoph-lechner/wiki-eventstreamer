import psycopg

def get_db_conn():
    # password in ~/.pgpass (remember to set mode=600)
    conn = psycopg.connect(dbname = 'wikidb', 
                           user = 'wikiproj_ro', 
                           host= '192.168.2.253',
                           port = 15432)
    return conn
