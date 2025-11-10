#!/usr/bin/env python3

# Prepare statistics queries for Streamlit

import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_freshness_deltat,get_freshness_abstimestamp,get_total_eventcount
from db_conn import get_db_conn
import pandas as pd




conn = get_db_conn()
# cur = conn.cursor()

# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

# passing something as value of 'since' currrently switches on hard-coded temporal cut
df = get_top_events(cur, wiki='enwiki', since='x')
print(df)

print('== freshness ==')
print('absolute timestamp of most recent event in DB: '+get_freshness_abstimestamp(cur))
print('age of this event in seconds: ' + f'{get_freshness_deltat(cur)}')
print('total number of events in DB: ' + f'{get_total_eventcount(cur)}')
