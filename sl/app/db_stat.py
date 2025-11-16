import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_freshness_deltat,get_freshness_getoldest_abs,get_freshness_abs,get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st

st.set_page_config(page_title="database statistics", page_icon=":material/table:")

conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

"""
# Database Infos
On this page, a few statistics about the underlying database are compiled.
"""

# timezones in Python: https://stackoverflow.com/a/12204612

st.write('## DB Freshness Infos')
with st.spinner("Preparing statistics..."):
    st.write('* The DB covers the time range (times in UTC): '
        + get_freshness_getoldest_abs(cur).isoformat() + ' -- '
        + get_freshness_abs(cur).isoformat())
    st.write('* Age of this event in seconds: ' + f'{get_freshness_deltat(cur)}')

st.write('## DB Stats')
with st.spinner("Preparing statistics..."):
    st.write('Total number of events in DB: ' + f'{get_total_eventcount(cur)}')

