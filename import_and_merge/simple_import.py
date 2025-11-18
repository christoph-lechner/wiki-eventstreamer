#!/usr/bin/env python3

import psycopg
import json
import argparse
import gzip
import datetime

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

data_table = 'wiki_change_events_test';
stg_table_prefix = 'stg_tmp';
do_debug = False

### parse user-provided settings ###
parser = argparse.ArgumentParser(
                    prog='simple_import',
                    description='Simple wiki event importer')

parser.add_argument('filename') # positional argument
parser.add_argument('-z', '--gzip', action='store_true')

args = parser.parse_args()
# print(args)

# helper function so we can use "with ... as fin" for both modes
def open_infile():
    print(f'Input file: {args.filename}')
    if args.gzip:
        return gzip.open(args.filename,'r')
    else:
        return open(args.filename,'rb')

#conn = psycopg.connect(dbname = 'postgres', 
#                       user = 'postgres', 
#                       host= 'localhost',
#                       password = "postgres",
#                       port = 5432)
conn = psycopg.connect(dbname = 'wikidb', 
                       user = 'postgres', 
                       host= 'localhost',
                       password = "postgres",
                       port = 15432)

# obtain cursor to perform database operations
cur = conn.cursor()

# make sure that names of temporary tables are pretty unique
tnow = datetime.datetime.now()
stg_table_prefix = stg_table_prefix+'_'+tnow.strftime('%Y%m%dT%H%M%S_%f')
stg_table_load   = stg_table_prefix+'_1';
stg_table_step2  = stg_table_prefix+'_2';
stg_table_step3  = stg_table_prefix+'_3';

# CREATE TEMPORARY TABLE -> table is automatically dropped at end of transaction
# For debugging we don't want that...
if do_debug:
    flag_temp = ''
else:
    flag_temp = 'TEMPORARY'

cur.execute(
f"""
CREATE {flag_temp} TABLE {stg_table_load}(
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
)

linecntr=0
with open_infile() as fin:
    for l_ in fin:
        l_ = l_.decode() # we use file in 'rb' mode now so we can switch transparently between gzip'd and standard files
        linecntr += 1
        if (linecntr%100000)==0:
            print('.', end='', flush=True)
        #
        try:
            event = json.loads(l_)
        except ValueError:
            continue

        #print(event)
        if (not 'meta' in event):
            print('skipping event: not all fields present')
            continue

        # Extract information from event
        # See schema in directory schema/
        # Sometimes, not all fields are present
        # Missing elements in decoded JSON string are replaced by None,
        # resulting in NULL in DB
        def my_helper(dict,key):
            if not key in dict:
                # print(f'N for {key}')
                return None
            return dict[key]
        event_meta_dt     = my_helper(event['meta'],'dt')
        event_meta_id     = my_helper(event['meta'],'id')
        event_meta_domain = my_helper(event['meta'],'domain')
        event_id = my_helper(event,'id')
        event_wiki = my_helper(event,'wiki')
        event_title = my_helper(event,'title')
        event_user = my_helper(event,'user')
        event_bot = my_helper(event,'bot')
        event_type = my_helper(event,'type')

        # todo: check format string for int value (8-byte int in DB)
        cur.execute('INSERT INTO '+stg_table_load+' (event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (event_meta_dt, event_meta_id, event_meta_domain, event_id, event_type, event_wiki, event_user, event_bot, event_title))
        # break

print('') # newline
print(f'Loaded {linecntr} events')
rowcount_file = linecntr

#####

print('adding hashes to rows ...')
cur.execute(
f"""
CREATE {flag_temp} TABLE {stg_table_step2} AS
SELECT
	MD5(CONCAT(CONCAT(event_meta_id,'_'),'-',CONCAT(event_meta_dt,'_'),'-',CONCAT(CAST(event_id AS TEXT),'_'),'-',CONCAT(event_user,'_'))) AS _h,
	TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS.FF3 TZ') AS ts_event_meta_dt,
	event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title
FROM {stg_table_load};
"""
)
rowcount_initial = cur.rowcount # no deduplication here, so it should correspond to number of loaded rows

print('deduplicate staged rows bashed on hashes (sometimes the same event is sent multiple times) + drop canary events ...')
cur.execute(
f"""
-- de-duplicate based on MD5 hash
CREATE {flag_temp} TABLE {stg_table_step3} AS
WITH q AS (
	SELECT *, ROW_NUMBER() OVER(PARTITION BY _h) AS _rn FROM {stg_table_step2}
)
SELECT
    _h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title
FROM q WHERE
	_rn=1
	-- discard 'canary' events (see https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service)
	AND event_meta_domain<>'canary';
"""
)
rowcount_hash_dedupl = cur.rowcount

# finally MERGE only rows with unseen hash values
# -> loading the same data twice does not harm as nothing gets inserted
print('execute MERGE command (only events with new MD5 hash get stored)')
cur.execute(
f"""
MERGE
INTO
    {data_table} AS dst
USING
    {stg_table_step3} AS src
ON
	dst._h=src._h
WHEN MATCHED THEN DO NOTHING
WHEN NOT MATCHED THEN INSERT VALUES (_h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title);
"""
)
rowcount_final_merge = cur.rowcount

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
