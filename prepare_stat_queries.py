#!/usr/bin/env python3

# Prepare statistics queries for Streamlit

import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count
from db_conn import get_db_conn
import pandas as pd

###########################
### Obtain data from DB ###
###########################


conn = get_db_conn()
# cur = conn.cursor()

# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

cur.execute(
"""
SELECT
   event_title,COUNT(*) AS c
FROM wiki_change_events_test
WHERE 
   event_type='edit' AND event_wiki='enwiki' 
   AND (NOT event_title LIKE 'Talk:%')
   AND (NOT event_title LIKE 'User:%') AND (NOT event_title LIKE 'User talk:%')
   AND (NOT event_title LIKE 'Wikipedia:%') AND (NOT event_title LIKE 'Wikipedia talk:%')
GROUP BY event_title
ORDER BY COUNT(*) DESC
LIMIT 20;
"""
)
res_rows = cur.fetchall()
accu_data_title=[]
accu_data_counts=[]
for row in res_rows:
    # print(row)
    accu_data_title.append(row['event_title'])
    accu_data_counts.append(row['c'])

accu_data = {
    'title': accu_data_title,
    'c': accu_data_counts,
}


df = pd.DataFrame.from_dict(data=accu_data)
print(df)



def get_freshness_abstimestamp():
    # add index to db speeds up this query:
    # CREATE INDEX wiki_change_events_test_ts_event_meta_dt_idx ON wiki_change_events_test (ts_event_meta_dt);
    cur.execute(
        "SELECT MAX(ts_event_meta_dt) AS max_ts FROM wiki_change_events_test;"
    )
    res = cur.fetchone()
    # in the database the timestamps are stored in UTC, let's obtain string in local timezone
    str_localtime = res['max_ts'].astimezone().isoformat()
    return str_localtime

def get_freshness_deltat():
    cur.execute(
        "SELECT (NOW()-MAX(ts_event_meta_dt)) AS freshness FROM wiki_change_events_test;"
    )
    res = cur.fetchone()
    print(res['freshness'])
