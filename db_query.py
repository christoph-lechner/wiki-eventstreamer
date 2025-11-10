# CL, 2025-Nov-10

import psycopg
import json
import datetime
import time

def get_totaledit_count(cur, wiki = 'enwiki'):
    q_wiki = wiki

    cur.execute(
        """
        SELECT
           DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
           COUNT(*)
        FROM wiki_change_events_test
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
        r_date = row[0]
        r_hour = int(row[1]) # cast to int to get rid of Decimal.decimal type
        r_value = int(row[2])
        # https://stackoverflow.com/q/1937622
        r_dt = datetime.datetime(year=r_date.year,month=r_date.month,day=r_date.day,hour=r_hour)
        accu_data.append({'t':r_dt, 'value':r_value})

    return(accu_data)


def get_edit_count(cur, wiki = 'enwiki', title = 'UPS Airlines Flight 2976'):
    q_wiki = wiki
    q_title = title

    cur.execute(
        """
        WITH q AS (
            SELECT
               DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
               COUNT(*),
                -- To determine time range for zero-gap filling in result
                -- MIN(ts_event_meta_dt) AS col_min, MAX(ts_event_meta_dt) AS col_max,
                -- need start of hour, see https://www.postgresql.org/docs/current/functions-datetime.html
                DATE_TRUNC('HOUR', MIN(ts_event_meta_dt)) AS col_min_startofhour
            FROM wiki_change_events_test
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
                    (SELECT MIN(col_min_startofhour) FROM q),
                    (SELECT MAX(col_min_startofhour) FROM q),
                    interval '1 hour'
                ) AS gs
        )
        SELECT
            -- column for development purposes in pgadmin
            -- gs_date,gs_hour,q.date,q.hour,COALESCE(q.count,-10) FROM times_without_gap
            -- the gs_* columns are not-NULL
            gs_date,gs_hour,COALESCE(q.count,-10) FROM times_without_gap
        LEFT JOIN q ON (q.date=gs_date AND q.hour=gs_hour);
        """,
        (q_wiki,q_title)
    )

    res_rows = cur.fetchall()
    accu_data=[]
    for row in res_rows:
        r_date = row[0]
        r_hour = int(row[1]) # cast to int to get rid of Decimal.decimal type
        r_value = int(row[2])
        # https://stackoverflow.com/q/1937622
        r_dt = datetime.datetime(year=r_date.year,month=r_date.month,day=r_date.day,hour=r_hour)
        accu_data.append({'t':r_dt, 'value':r_value})

    return(accu_data)
