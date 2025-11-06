#!/usr/bin/env python3

import psycopg
import json

"""
CREATE TABLE wtbl(
	event_meta_dt TEXT,
	event_meta_id TEXT,
	event_meta_domain TEXT,
    event_id BIGINT,
	event_wiki TEXT,
    event_title TEXT,
	event_user TEXT,
	event_type TEXT
);
"""

"""
SELECT event_meta_dt,TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') FROM wtbl LIMIT 10;
"""

# zcat changes__starting20251105T1630_finaltest.txt.gz | head -n 1000000 > events_in.json
# ./simple_import.py

conn = psycopg.connect(dbname = 'postgres', 
                       user = 'postgres', 
                       host= 'localhost',
                       password = "postgres",
                       port = 5432)

# obtain cursor to perform database operations
cur = conn.cursor()

linecntr=0
with open('events_in.json','r') as fin:
    for l_ in fin:
        linecntr+=1
        if (linecntr%100000)==0:
            print('.')
        #
        try:
            event = json.loads(l_)
        except ValueError:
            continue

        #print(event)
        if (not 'meta' in event):
            print('skipping event: not all fields present')
            continue

        # Sometimes, not all fields are present
        # Missing elements in decoded JSON string are replaced by None, resulting in NULL in DB
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
        event_type = my_helper(event,'type')

        # todo: check format string for int value (8-byte int in DB)
        cur.execute('INSERT INTO wtbl (event_meta_dt,event_meta_id,event_meta_domain,event_id,event_wiki,event_title,event_user,event_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (event_meta_dt, event_meta_id, event_meta_domain, event_id, event_wiki, event_title, event_user, event_type))
        # break

conn.commit()

cur.close()
conn.close()
