#!/usr/bin/env python3

# Christoph Lechner, 2025-Nov

import psycopg
import json
import argparse
import gzip
import datetime
from wikiloader import WikiLoader

"""
Outdated schema of table holding all data (after merging all loads):
CREATE TABLE wiki_change_events(
    -- MD5 hash over a few fields, ensures deduplication (data is loaded into this table using MERGE command)
    _h TEXT UNIQUE,
    ts_event_meta_dt TIMESTAMP WITH TIME ZONE,
	event_meta_dt TEXT,
	event_meta_id TEXT,
	event_meta_domain TEXT,
    event_id BIGINT,
	event_type TEXT,
	event_wiki TEXT,
	event_user TEXT,
    event_bot BOOLEAN,
    event_title TEXT
);
"""


### parse user-provided settings ###
parser = argparse.ArgumentParser(
                    prog='simple_import',
                    description='Simple wiki event importer')

parser.add_argument('filename') # positional argument
parser.add_argument('-z', '--gzip', action='store_true')

args = parser.parse_args()
# print(args)


# Password in ~/.pgpass, line format
# hostname:port:database:username:password
# !mode has to be 600!
conn = psycopg.connect(dbname = 'dev', 
                       user = 'dev', 
                       host= '192.168.2.253',
                       port = 15432)

# obtain cursor to perform database operations
cur = conn.cursor()

wl = WikiLoader()
rowcount_file = wl.data_load(cur,args.filename,args.gzip)
rowcount_initial = wl.data_addhashes(cur) # no deduplication here, so it should correspond to number of loaded rows
rowcount_hash_dedupl = wl.data_dedupl(cur)
rowcount_final_merge = wl.data_merge(cur)
conn.commit()
cur.close()

#############################################################
### LOADING AND MERGING COMPLETE                          ###
### UPDATE MATERIALIZED VIEWS                             ###
### For the current development phase: to be more robust, ###
### we do this in a second transaction                    ###
#############################################################

from util_advtime import MyTimer

# obtain cursor to perform database operations
cur = conn.cursor()

def update_matview(conn,cur,viewname):
    @MyTimer.timeit(infotxt=f'Update {viewname}')
    def worker(conn,cur,viewname):
        """
        Function that does the actual work. Added this to be able to use
        wrapper with parameter depending on argument to the outer function.
        """
        print(f'Updating view {viewname} ...')
        cur.execute(f'REFRESH MATERIALIZED VIEW {viewname};')

    worker(conn,cur,viewname)


# for schema, see demo.py
def cb_report(conn,cur,s):
    infotxt = None
    if 'infotxt' in s:
        infotxt = s['infotxt']
    
    cur.execute('INSERT INTO wiki_loaderperfdata (tstart,dur,func,infotxt) VALUES (%s,%s,%s,%s)', (s['tstart'],s['dur'],s['func'],infotxt))
    # print(s)



matviews_to_update = ['wiki_matview_countsall', 'wiki_matview_countsedits']
for cur_view in matviews_to_update:
    update_matview(conn,cur,cur_view)

# After updating the materialized views, commit
conn.commit()

# Storing of the collected statistical information should be done in
# a separate transaction. If something goes wrong, it does not break
# the operation of the main program.
print('Storing collected time stats')
with conn.transaction():
    MyTimer.report1(lambda obj: cb_report(conn,cur,obj))

conn.commit()
cur.close()
conn.close()

print(f'DONE: {rowcount_final_merge}/{rowcount_file} rows from file got merged into data table')
print(f'   breakdown: from file: {rowcount_file}; after dedupl. {rowcount_hash_dedupl}; rows merged {rowcount_final_merge}')
