import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_freshness_deltat,get_freshness_abstimestamp,get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st

st.set_page_config(page_title="databse statistics", page_icon=":material/table:")

conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

st.write('# Top20: Edits')
"""
This is a list of articles in the English edition of Wikipedia that saw most edits since 2025-11-10, 00:00:01 UTC.
"""
df = get_top_events(cur, wiki='enwiki', since='x')
df
