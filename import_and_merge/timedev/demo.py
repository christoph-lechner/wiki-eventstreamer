#!/usr/bin/env python3

# Christoph Lechner, 2025-11-16
# Stores timing information into DB
# Preparation for updating materialized views

import psycopg
import time
from util_advtime import MyTimer

"""
CREATE TABLE wiki_loaderperfdata(
	tstart timestamp with time zone,
	dur float,
	func text,
	infotxt text
)
"""

def update_matview(viewname):
    @MyTimer.timeit(infotxt=f'Update {viewname}')
    def worker(viewname):
        """
        Function that does the actual work. Added this to be able to use
        wrapper with parameter depending on argument to the outer function.
        """
        print(f'{viewname}')
        time.sleep(1)

    worker(viewname)

matviews_to_update = ['wiki_matview_countsall', 'wiki_matview_countsedits']

for cur_view in matviews_to_update:
    update_matview(cur_view)

def cb_report(conn,cur,s):
    print(conn)
    infotxt = None
    if 'infotxt' in s:
        infotxt = s['infotxt']
    
    cur.execute('INSERT INTO wiki_loaderperfdata (tstart,dur,func,infotxt) VALUES (%s,%s,%s,%s)', (s['tstart'],s['dur'],s['func'],infotxt))
    print(s)




conn = psycopg.connect(dbname = 'wikidb', 
                       user = 'postgres', 
                       host= '192.168.2.253',
                       password = "postgres",
                       port = 15432)

# obtain cursor to perform database operations
cur = conn.cursor()

# Storing of the collected statistical information should be done in
# a separate transaction. If something goes wrong, it does not break
# the operation of the main program.
print('Collected time stats: ')
MyTimer.report1(lambda obj: cb_report(conn,cur,obj))

conn.commit()
cur.close()
conn.close()
