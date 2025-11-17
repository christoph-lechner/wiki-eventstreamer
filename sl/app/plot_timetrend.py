import psycopg
import datetime
import time
from db_query import get_totaledit_count, get_edit_count, get_top_events, get_total_eventcount
from db_conn import get_db_conn
import pandas as pd
import streamlit as st
import plotly.express as px
import itertools

use_materialized=True

def worker():
    # caching: not needed when taking data from materialized views
    # @st.cache_data(ttl=600)
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
    #
    with_user_defined_timerange = st.checkbox('enter date range to plot', False)
    user_def_timerange_start = None
    user_def_timerange_end = None
    if with_user_defined_timerange:
        st.write('Enter the date range to plot (Note: as of now, you can specify the days, the time is always assumed to be midnight UTC)')
        user_def_timerange_start = st.date_input('start date', datetime.datetime.today() - datetime.timedelta(days=7))
        user_def_timerange_end = st.date_input('end date (including this day)', datetime.datetime.today())
        if user_def_timerange_start+datetime.timedelta(days=1)>user_def_timerange_end:
            st.error('Provided dates have to meet the following: Start date earlier than end date; minimum length of time interval: 1 day. Adjusting start date accordingly.')
            user_def_timerange_start = user_def_timerange_end - datetime.timedelta(days=1)

    # st.write(f'{user_def_timerange_start} -- {user_def_timerange_end}')

    ### input sanitization (accept only wikis that we know) ###
    selected_wikis = [_ for _ in selected_wikis if _ in set(avail_wikis)]
    n_selected_wikis = len(selected_wikis)
    if not selected_wikis:
        st.error('Please select at least one wiki.')
        return

    #######################
    ### build sql query ###
    #######################
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

    # when computing everything from scratch (makes app less responsive)
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

    # when using materialized statistical data
    def execquery_mat():
        if with_bots:
            use_col = 'count_bot_flagignore'
        else:
            use_col = 'count_bot_false'
        cntr=1
        def_cntrcols = []
        query_args = []
        query_args_cols = []
        pd_colmap = {} # for naming colums in pandas DataFrame (for plot preparation)
        for w in selected_wikis:
            # NOTE: the actual string values are not inserted here (to exluce any risk for SQL injection)
            def_cntrcols.append(f'SUM((CASE WHEN event_wiki=%s THEN {use_col} END)) AS c{cntr}')
            query_args_cols.append(w)
            pd_colmap[f'c{cntr}'] = w
            cntr+=1

        qstr = 'SELECT date,hour,'
        qstr += ','.join(def_cntrcols)
        qstr += ' FROM wiki_matview_countsedits '
        qstr += "WHERE event_wiki IN (" +(','.join(n_selected_wikis*['%s']))+ ") "
        query_args = 2*query_args_cols # duplicate the list: first for column definition ("SUM(...)"), secondly for "WHERE event_wiki IN (...)"
        # if user-defined time ranges are provided, add placeholders to the query (and simultaneously the data to the list of arguments)
        if user_def_timerange_start:
            qstr += " AND date>=%s "
            query_args.append(user_def_timerange_start)
        if user_def_timerange_end:
            qstr += " AND date<=%s "
            query_args.append(user_def_timerange_end)
        qstr += 'GROUP BY date,hour ORDER BY date,hour;'
        # print(qstr)
        cur.execute(qstr, query_args)
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

    iter_color = itertools.cycle(plt_colors)

    fig = px.line(df, x='ts', y=selected_wikis, log_y=with_ylog, color_discrete_sequence=list(itertools.islice(iter_color, len(selected_wikis))) )
    fig.update_layout(xaxis_title='time', yaxis_title='edits/hour', legend=dict(
        orientation='h', title_text='wiki', yanchor='bottom', y=1.02, xanchor='right', x=1.0
    ))
    st.plotly_chart(fig, theme='streamlit')

#####
#####
#####

st.set_page_config(page_title="Edits: Time Trends", page_icon=":material/table:")


conn = get_db_conn()
# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)

st.write('# Edits: Time Trends')
with st.spinner("Preparing statistics..."):
    worker()

# It is very important to close the DB connection.
# Otherwise, refreshing the materialized views will not start until streamlit program was terminated. (Symptoms: execution of query takes forever, no postgres CPU load on DB server)
cur.close()
conn.close()
