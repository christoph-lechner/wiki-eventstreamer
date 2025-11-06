#!/usr/bin/env python3

import psycopg
import json

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

# zcat changes__starting20251105T1630_finaltest.txt.gz | head -n 1000000 > events_in.json
# ./simple_import.py

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
with open('events_in.json','r') as fin:
    for l_ in fin:
        linecntr+=1
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

conn.commit()

cur.close()
conn.close()
