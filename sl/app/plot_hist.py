#!/usr/bin/env python3

import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_freshness_deltat,get_freshness_abstimestamp,get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Edits over time", page_icon=":material/table:")

conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor()





def getit(dataspec):
    t_datacollection0 = time.time()
    plotdata = []
    for kwargs in dataspec:
        my_data = {}
        my_data['data'] = get_edit_count(cur, **kwargs)
        my_data['infotxt'] = kwargs['wiki']+'/'+kwargs['title']
        # print(my_data)
        plotdata.append(my_data)
    t_datacollection1 = time.time()
    print(f'time for data collection: {t_datacollection1 - t_datacollection0}')

    df = pd.DataFrame.from_dict(data=my_data['data'])
    return(df)



"""
### Edits for "2025 New York City mayoral election" in enwiki
"""
# Dataset of interest
# dict format as needed to pass as **kwargs
dataspec = [
    {'wiki':'enwiki', 'title':'2025 New York City mayoral election'},
]
df = getit(dataspec)
st.line_chart(df, x='t', y='value', x_label='Date/Time', y_label='Changes / Hour')


"""
### Edits for "Wolfgang Amadeus Mozart" in dewiki
"""
dataspec = [
    {'wiki':'dewiki', 'title':'Wolfgang Amadeus Mozart'},
]
df = getit(dataspec)
st.line_chart(df, x='t', y='value', x_label='Date/Time', y_label='Changes / Hour')


