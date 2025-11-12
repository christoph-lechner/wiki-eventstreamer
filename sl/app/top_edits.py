import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_freshness_deltat,get_freshness_abstimestamp,get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Top20", page_icon=":material/table:")

conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

st.write('# Top20: Edits')
"""
This is a list of articles in the English edition of Wikipedia that saw most edits since 2025-11-10, 00:00:01 UTC.
"""
with st.spinner("Preparing statistics..."):
    df = get_top_events(cur, wiki='enwiki', since='x')
    df


#########################
### from plot_hist.py ###
#########################
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


st.write(
"""
## History plots first the first pages in the list
Some of these pages might have been created only very recently.
Therefore, the plots may habe different time spans (horizontal axis).

**TODO:** Rework so that the traces are plotted over the same time axis.
"""
)

row_cntr=0
for row in df.iterrows():
    row_cntr += 1
    if row_cntr>10:
        break

    title = row[1]['title']
    print(title)

    st.write(
        f"""
        ### Edits for Pos {row_cntr}: "{title}" in enwiki
        """
    )
    # Dataset of interest
    # dict format as needed to pass as **kwargs
    dataspec = [
        # {'wiki':'enwiki', 'title':'2025 New York City mayoral election'},
        {'wiki':'enwiki', 'title':title},
    ]
    df = getit(dataspec)
    st.line_chart(df, x='t', y='value', x_label='Date/Time', y_label='Changes / Hour')

