import psycopg

def get_db_conn():
    #conn = psycopg.connect(dbname = 'postgres', 
    #                       user = 'postgres', 
    #                       host= 'localhost',
    #                       password = "postgres",
    #                       port = 5432)
    conn = psycopg.connect(dbname = 'wikidb', 
                           user = 'postgres', 
                           host= '192.168.2.253',
                           password = "postgres",
                           port = 15432)
    return conn
