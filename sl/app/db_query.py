# CL, 2025-Nov-10

import psycopg
import json
import datetime
import time
import pandas as pd


# NOTE: these functions expect cursor with row_factory=dict_row:
# cur = conn.cursor(row_factory=dict_row)


def get_totaledit_count(cur, wiki = 'enwiki'):
    q_wiki = wiki

    cur.execute(
        """
        SELECT
           DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
           COUNT(*) AS c
        FROM wiki_change_events
        WHERE
           event_type='edit' AND event_wiki=%s
        GROUP BY DATE(ts_event_meta_dt), EXTRACT(HOUR FROM ts_event_meta_dt)
        ORDER BY DATE(ts_event_meta_dt), EXTRACT(HOUR FROM ts_event_meta_dt)
        """,
        (q_wiki,) # !extra comma to pass tuple!
    )

    res_rows = cur.fetchall()
    accu_data=[]
    for row in res_rows:
        r_date = row['date']
        r_hour = int(row['hour']) # cast to int to get rid of Decimal.decimal type
        r_value = int(row['c'])
        # https://stackoverflow.com/q/1937622
        r_dt = datetime.datetime(year=r_date.year,month=r_date.month,day=r_date.day,hour=r_hour)
        accu_data.append({'t':r_dt, 'value':r_value})

    return(accu_data)


def get_edit_count(cur, wiki = 'enwiki', title = 'UPS Airlines Flight 2976', timerange_min=None, timerange_max=None):
    q_wiki = wiki
    q_title = title

    def helper_timerange(timerange_arg, minmax):
        if timerange_arg is None:
            if minmax=='max':
                return '(SELECT MAX(col_min_startofhour) FROM q)'
            elif minmax=='min':
                return '(SELECT MIN(col_min_startofhour) FROM q)'
            else:
                raise ValueError('specify one of "min" or "max"')
        # also for instances of datetime.datetime, isinstance(..., datetime.date) -> True
        if not isinstance(timerange_arg, datetime.date):
            raise ValueError()
        return "'"+str(timerange_arg)+"'"


    cur.execute(
        f"""
        WITH q AS (
            SELECT
               DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
               COUNT(*) AS c,
                -- To determine time range for zero-gap filling in result
                -- MIN(ts_event_meta_dt) AS col_min, MAX(ts_event_meta_dt) AS col_max,
                -- need start of hour, see https://www.postgresql.org/docs/current/functions-datetime.html
                DATE_TRUNC('HOUR', MIN(ts_event_meta_dt)) AS col_min_startofhour
            FROM wiki_change_events
            WHERE
               event_type='edit' AND event_wiki=%s AND event_title=%s
            GROUP BY
               DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
            ORDER BY
               DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
        ),
        times_without_gap AS(
        SELECT
                DATE(gs) AS gs_date, EXTRACT(HOUR FROM gs) AS gs_hour
        FROM
                generate_series(
                    -- (SELECT MIN(col_min_startofhour) FROM q),
                    {   helper_timerange(timerange_min,'min')   }  ,
                    -- (SELECT MAX(col_min_startofhour) FROM q),
                    {   helper_timerange(timerange_max,'max')   }  ,
                    interval '1 hour'
                ) AS gs
        )
        SELECT
            -- column for development purposes in pgadmin
            -- gs_date,gs_hour,q.date,q.hour,COALESCE(q.count,-10) FROM times_without_gap
            -- the gs_* columns are not-NULL
            gs_date,gs_hour,COALESCE(q.c,0) AS c FROM times_without_gap
        LEFT JOIN q ON (q.date=gs_date AND q.hour=gs_hour);
        """,
        (q_wiki,q_title)
    )

    res_rows = cur.fetchall()
    accu_data=[]
    for row in res_rows:
        r_date = row['gs_date']
        r_hour = int(row['gs_hour']) # cast to int to get rid of Decimal.decimal type
        r_value = int(row['c'])
        # https://stackoverflow.com/q/1937622
        r_dt = datetime.datetime(year=r_date.year,month=r_date.month,day=r_date.day,hour=r_hour)
        accu_data.append({'t':r_dt, 'value':r_value})

    return(accu_data)


###########################
### STATISTICAL QUERIES ###
###########################


# FIXME: update table name ("_test" no longer correct)
# add index to db speeds up this query:
# CREATE INDEX wiki_change_events_test_ts_event_meta_dt_idx ON wiki_change_events_test (ts_event_meta_dt);
def get_freshness_getoldest_abs(cur):
    cur.execute(
        "SELECT MIN(ts_event_meta_dt) AS min_ts FROM wiki_change_events;"
    )
    res = cur.fetchone()
    return res['min_ts']

def get_freshness_abs(cur):
    cur.execute(
        "SELECT MAX(ts_event_meta_dt) AS max_ts FROM wiki_change_events;"
    )
    res = cur.fetchone()
    return res['max_ts']

def get_freshness_deltat(cur):
    cur.execute(
        "SELECT (NOW()-MAX(ts_event_meta_dt)) AS freshness FROM wiki_change_events;"
    )
    res = cur.fetchone()
    # time diff is returned as 'datetime.timedelta'
    return (res['freshness'].total_seconds())

# FIXME: expensive on Google BigQuery
def get_total_eventcount(cur):
    cur.execute(
        "SELECT COUNT(*) AS nevents FROM wiki_change_events;"
    )
    res = cur.fetchone()
    return (res['nevents'])

def get_top_events(cur, wiki='enwiki', since=None):
    if since is None:
        str_since = '1900-01-01'
    else:
        # FIXME: hardcoded
        str_since = '2025-11-10'

    # TODO: for dewiki we want to exclude different article title prefixes than for enwiki
    cur.execute(
        """
        SELECT
           event_title,COUNT(*) AS c
        FROM wiki_change_events
        WHERE
           ts_event_meta_dt>=%s
           AND event_type='edit' AND event_wiki=%s
           AND (NOT event_title LIKE 'Talk:%%')
           AND (NOT event_title LIKE 'User:%%') AND (NOT event_title LIKE 'User talk:%%')
           AND (NOT event_title LIKE 'Wikipedia:%%') AND (NOT event_title LIKE 'Wikipedia talk:%%')
        GROUP BY event_title
        ORDER BY COUNT(*) DESC
        LIMIT 20;
        """,
        (str_since,wiki)
    )

    # for pandas DataFrame we need a "dictionary of lists", not a "list of dictionaries" (which would be better design IMO)
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
    return(df)

