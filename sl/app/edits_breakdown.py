import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st
import plotly.express as px
import itertools

def worker():
    def query_withbots():
        cur.execute(
        """
        WITH q AS (
            SELECT
                event_wiki,
                SUM(count_bot_flagignore) AS sum_bot_flagignore,
                SUM(count_bot_true) AS sum_bot_true,
                SUM(count_bot_false) AS sum_bot_false
            FROM wiki_matview_countsall
            WHERE date>='2025-11-16'
            GROUP BY event_wiki
        ), totals AS (
            SELECT
                SUM(sum_bot_flagignore) AS tot_bot_flagignore,
                SUM(sum_bot_true) AS tot_bot_true,
                SUM(sum_bot_false) AS tot_bot_false
            FROM q
        )
        SELECT
            event_wiki,
            sum_bot_flagignore AS sum,
            sum_bot_flagignore/totals.tot_bot_flagignore AS rel_sum,
            SUM(sum_bot_flagignore) OVER (ORDER BY sum_bot_flagignore DESC,event_wiki ASC) AS cumsum,
            (SUM(sum_bot_flagignore) OVER (ORDER BY sum_bot_flagignore DESC,event_wiki ASC))/totals.tot_bot_flagignore AS rel_cumsum
        FROM q,totals;
        """
        )
    def query_nobots():
        # query created from query for case 'ignorebots'
        # -> FIXME: check if everything was replaced correctly
        cur.execute(
        """
        WITH q AS (
            SELECT
                event_wiki,
                SUM(count_bot_flagignore) AS sum_bot_flagignore,
                SUM(count_bot_true) AS sum_bot_true,
                SUM(count_bot_false) AS sum_bot_false
            FROM wiki_matview_countsall
            WHERE date>='2025-11-16'
            GROUP BY event_wiki
        ), totals AS (
            SELECT
                SUM(sum_bot_flagignore) AS tot_bot_flagignore,
                SUM(sum_bot_true) AS tot_bot_true,
                SUM(sum_bot_false) AS tot_bot_false
            FROM q
        )
        SELECT
            event_wiki,
            sum_bot_false AS sum,
            sum_bot_false/totals.tot_bot_flagignore AS rel_sum,
            SUM(sum_bot_false) OVER (ORDER BY sum_bot_false DESC,event_wiki ASC) AS cumsum,
            (SUM(sum_bot_false) OVER (ORDER BY sum_bot_false DESC,event_wiki ASC))/totals.tot_bot_false AS rel_cumsum
        FROM q,totals;
        """
        )

    with_bots = st.checkbox('Also count changes by "bots"', True)
    if with_bots:
        query_withbots()
    else:
        query_nobots()

    res_rows = cur.fetchall()
    df = pd.DataFrame(res_rows)
    # Display only the largest wikis contributing to a total 95% of edit events
    df.loc[df['rel_cumsum']>0.95, 'event_wiki'] = 'other wikis'
    st.write('Only displaying largest wikis contributing to a total of 95 percent of all edit events (all others are indicated as "other wikis")')

    # FIXME: canary events have event_wiki=None
    # -> causes issues with treemap
    # -> On 2025-11-18 fixed import script to discard canary events (thus these will not be an issue in the future)
    df = df.dropna(subset=['event_wiki'])
    fig = px.treemap(
        df,
        path=["event_wiki"],      # single-level = flat treemap
        values="rel_sum",
        color="rel_sum",    # optional
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, theme='streamlit')

#####
#####
#####

st.set_page_config(page_title="Edits: Breakdown", page_icon=":material/table:")


conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

st.write('# Edits: Breakdown')
st.write('Info: currently with hard-coded time range (everything after 2025-11-16)')
with st.spinner("Preparing statistics..."):
    worker()

# It is very important to close the DB connection.
# Otherwise, refreshing the materialized views will not start until streamlit program was terminated. (Symptoms: execution of query takes forever, no postgres CPU load on DB server)
cur.close()
conn.close()
