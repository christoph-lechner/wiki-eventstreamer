#!/usr/bin/env python3

import psycopg
import json
import datetime

"""
CREATE TABLE wtbl(
	event_meta_dt TEXT,
	event_meta_id TEXT,
	event_meta_domain TEXT,
    event_id BIGINT,
	event_type TEXT,
	event_wiki TEXT,
	event_user TEXT,
    event_bot BOOLEAN,
    event_title TEXT
);
"""

# zcat changes__starting20251105T1630_finaltest.txt.gz | head -n 1000000 > events_in.json
# ./simple_import.py

conn = psycopg.connect(dbname = 'postgres', 
                       user = 'postgres', 
                       host= 'localhost',
                       password = "postgres",
                       port = 5432)


def get_edit_count(wiki = 'enwiki', title = 'UPS Airlines Flight 2976'):
    q_wiki = wiki
    q_title = title

    cur = conn.cursor()

    cur.execute(
        """
        WITH q AS (
           SELECT
              TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS') AS ts_event_meta_dt,
              event_meta_id,event_meta_domain,event_id,event_wiki,event_user,event_type,event_title
           FROM wtbl
           WHERE
              event_type='edit' AND event_wiki=%s AND event_title=%s)
        SELECT
           DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
           COUNT(*)
        FROM q
        GROUP BY
           DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt)
        ORDER BY
           DATE(ts_event_meta_dt),EXTRACT(HOUR FROM ts_event_meta_dt);
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

###########################
### Obtain data from DB ###
###########################

# Datasets of interest
# dict format as needed to pass as **kwargs
dataspec = [
    {'wiki':'enwiki', 'title':'UPS Airlines Flight 2976'},
    {'wiki':'enwiki', 'title':'Zohran Mamdani'},
    {'wiki':'dewiki', 'title':'Wolfgang Amadeus Mozart'},
    {'wiki':'dewiki', 'title':'Zohran Mamdani'}
]

plotdata = []
for kwargs in dataspec:
    my_data = {}
    my_data['data'] = get_edit_count(**kwargs)
    my_data['infotxt'] = kwargs['wiki']+'/'+kwargs['title']
    plotdata.append(my_data)

#############
### Plots ###
#############

import matplotlib.pyplot as plt
import numpy as np

fig,hax = plt.subplots(1)

# latest time in database (FIXME: find from data)
dt_max = datetime.datetime(2025, 11, 6, 7, 0)
for curr_q in plotdata:
    curr_d = curr_q['data']
    # datatype: datetime.timedelta
    #           v-- earlier events <=> negative value (then they appear on the left of the time axis)
    plot_dt = [ -(dt_max-_['t']) for _ in curr_d ]
    plot_dt = [ _.total_seconds() for _ in plot_dt ]
    plot_v  = [ _['value'] for _ in curr_d ]
    #print(plot_dt)
    #print(plot_v)
    hax.plot(np.array(plot_dt)/3600.0,plot_v,'o--',label=curr_q['infotxt'])
    # break

hax.set_xlabel(f'time before {dt_max} [hours]')
hax.set_ylabel('edit count')
hax.legend()

# GROUP BY + aggregate function does not provide zero values for hours w/o any events
hax.set_title('Edit Counts (gaps in time-series not filled with zeros)')
plt.show()
