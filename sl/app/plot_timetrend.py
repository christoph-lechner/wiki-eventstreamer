import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Edits: Time Trends", page_icon=":material/table:")

conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

st.write('# Edits: Time Trends')

use_materialized=True

def worker():
    @st.cache_data(ttl=600)
    def get_list_of_wikis():
        if use_materialized:
            cur.execute(
                """
                SELECT event_wiki,SUM(count_bot_flagignore) AS c
                FROM wiki_matview_countsedits
                GROUP BY event_wiki
                ORDER BY SUM(count_bot_flagignore) DESC
                """
            )
        else:
            cur.execute(
                """
                SELECT event_wiki,COUNT(*) AS c
                FROM wiki_change_events_test
                WHERE event_type='edit'
                GROUP BY event_wiki
                ORDER BY COUNT(*) DESC;
                """
            )

        res_rows = cur.fetchall()
        avail_wikis = []
        for row in res_rows:
            avail_wikis.append(row['event_wiki'])
            # break
        return avail_wikis

    # user interface
    avail_wikis = get_list_of_wikis()
    selected_wikis = st.multiselect('Select Wikis to plot', avail_wikis,['enwiki','dewiki'])
    with_bots = st.checkbox('Also count changes by "bots"', True)
    with_ylog = st.checkbox('use vertical log scale', False)

    # input sanitization (accept only wikis that we know)
    selected_wikis = [_ for _ in selected_wikis if _ in set(avail_wikis)]
    n_selected_wikis = len(selected_wikis)
    if not selected_wikis:
        st.error('Please select at least one wiki.')
        return

    # Example query for four wikis selected:
    # SELECT
    #   DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
    #   SUM((CASE WHEN event_wiki='commonswiki' THEN 1 END)) AS c1,
    #   SUM((CASE WHEN event_wiki='wikidatawiki' THEN 1 END)) AS c2,
    #   SUM((CASE WHEN event_wiki='enwiki' THEN 1 END)) AS c3,
    #   SUM((CASE WHEN event_wiki='dewiki' THEN 1 END)) AS c4
    # FROM wiki_change_events_test
    # WHERE event_type='edit' AND event_wiki IN ('commonswiki','wikidatawiki','enwiki','dewiki')
    # GROUP BY date,hour
    # ORDER BY date,hour

    def execquery_notmat():
        cntr=1
        def_cntrcols = []
        query_args = []
        pd_colmap = {} # for naming colums in pandas DataFrame (for plot preparation)
        for w in selected_wikis:
            # NOTE: the actual string values are not inserted here (to exluce any risk for SQL injection)
            def_cntrcols.append(f'SUM((CASE WHEN event_wiki=%s THEN 1 END)) AS c{cntr}')
            query_args.append(w)
            pd_colmap[f'c{cntr}'] = w
            cntr+=1

        qstr = 'SELECT DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,'
        qstr += ','.join(def_cntrcols)
        qstr += ' FROM wiki_change_events_test '
        qstr += "WHERE event_type='edit' "
        # The streamreader rotates the stream dumps no at the full hour -> cut away the final (incomplete) hour
        qstr += " AND ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events_test) "
        # if requested, exclude edit events by clients identifying as bots (otherwise, ignore this flag)
        if not with_bots:
            qstr += ' AND event_bot=FALSE '
        qstr += " AND event_wiki IN (" +(','.join(n_selected_wikis*['%s']))+ ") "
        qstr += 'GROUP BY date,hour ORDER BY date,hour;'
        cur.execute(qstr, 2*query_args)
        res_rows = cur.fetchall()
        for r in res_rows:
            # r['ts'] = r['date']
            r['ts'] = datetime.datetime(r['date'].year,r['date'].month,r['date'].day) + datetime.timedelta(hours=int(r['hour']))

        df = pd.DataFrame(res_rows)
        df = df.rename(columns=pd_colmap)
        return(df)

    def execquery_mat():
        if with_bots:
            use_col = 'count_bot_flagignore'
        else:
            use_col = 'count_bot_false'
        cntr=1
        def_cntrcols = []
        query_args = []
        pd_colmap = {} # for naming colums in pandas DataFrame (for plot preparation)
        for w in selected_wikis:
            # NOTE: the actual string values are not inserted here (to exluce any risk for SQL injection)
            def_cntrcols.append(f'SUM((CASE WHEN event_wiki=%s THEN {use_col} END)) AS c{cntr}')
            query_args.append(w)
            pd_colmap[f'c{cntr}'] = w
            cntr+=1

        qstr = 'SELECT date,hour,'
        qstr += ','.join(def_cntrcols)
        qstr += ' FROM wiki_matview_countsedits '
        qstr += "WHERE event_wiki IN (" +(','.join(n_selected_wikis*['%s']))+ ") "
        qstr += 'GROUP BY date,hour ORDER BY date,hour;'
        # print(qstr)
        cur.execute(qstr, 2*query_args)
        res_rows = cur.fetchall()
        for r in res_rows:
            # r['ts'] = r['date']
            r['ts'] = datetime.datetime(r['date'].year,r['date'].month,r['date'].day) + datetime.timedelta(hours=int(r['hour']))

        df = pd.DataFrame(res_rows)
        df = df.rename(columns=pd_colmap)
        return(df)

    
    if use_materialized:
        df = execquery_mat()
    else:
        df = execquery_notmat()
    #print(df)
    # st.line_chart(df, x='ts', y=selected_wikis, x_label='Date/Time', y_label='Changes / Hour')

    # https://matplotlib.org/stable/gallery/color/color_cycle_default.html
    #import matplotlib.pyplot as plt
    #prop_cycle = plt.rcParams['axes.prop_cycle']
    #print(prop_cycle)
    plt_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    import itertools
    iter_color = itertools.cycle(plt_colors)

    import plotly.express as px
    fig = px.line(df, x='ts', y=selected_wikis, log_y=with_ylog, color_discrete_sequence=list(itertools.islice(iter_color, len(selected_wikis))) )
    fig.update_layout(xaxis_title='time', yaxis_title='edits/hour', legend=dict(
        orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1.0
    ))
    st.plotly_chart(fig, theme='streamlit')

#####
#####
#####

with st.spinner("Preparing statistics..."):
    worker()
