#!/usr/bin/env python3

import psycopg
import json
import argparse
import gzip

"""
CREATE TABLE wtbl(
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

# helper function so we can use "with ... as fin" for both modes
def open_infile():
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
        cur.execute('INSERT INTO wtbl (event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (event_meta_dt, event_meta_id, event_meta_domain, event_id, event_type, event_wiki, event_user, event_bot, event_title))
        # break

print('') # newline
conn.commit()
cur.close()
conn.close()

print(f'Loaded {linecntr} events')
