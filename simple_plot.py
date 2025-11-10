#!/usr/bin/env python3

import psycopg
import json
import datetime
import time

#conn = psycopg.connect(dbname = 'postgres', 
#                       user = 'postgres', 
#                       host= 'localhost',
#                       password = "postgres",
#                       port = 5432)
conn = psycopg.connect(dbname = 'wikidb', 
                       user = 'postgres', 
                       host= '192.168.2.253',
                       password = "postgres",
                       port = 15432)


def get_totaledit_count(wiki = 'enwiki'):
    q_wiki = wiki

    cur = conn.cursor()

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


def get_edit_count(wiki = 'enwiki', title = 'UPS Airlines Flight 2976'):
    q_wiki = wiki
    q_title = title

    cur = conn.cursor()

    cur.execute(
        """
        WITH q AS (
            SELECT
               DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
               COUNT(*)
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
                generate_series((SELECT MIN(date) FROM q), (SELECT MAX(date) FROM q), interval '1 hour') AS gs
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

###########################
### Obtain data from DB ###
###########################

# Datasets of interest
# dict format as needed to pass as **kwargs
dataspec = [
    {'wiki':'enwiki', 'title':'UPS Airlines Flight 2976'},
    {'wiki':'enwiki', 'title':'Zohran Mamdani'},
    {'wiki':'dewiki', 'title':'Zohran Mamdani'},
    {'wiki':'enwiki', 'title':'2025 New York City mayoral election'},
    {'wiki':'dewiki', 'title':'Wolfgang Amadeus Mozart'},
    # last edit of en. Mozart article was on Nov 1, 2025 (i.e. outside of our data range)
    {'wiki':'enwiki', 'title':'Wolfgang Amadeus Mozart'},
    {'wiki':'enwiki', 'title':'Pauline Collins'},
    {'wiki':'enwiki', 'title':'Timeline of file sharing'},
]


t_datacollection0 = time.time()
plotdata = []
for kwargs in dataspec:
    my_data = {}
    my_data['data'] = get_edit_count(**kwargs)
    my_data['infotxt'] = kwargs['wiki']+'/'+kwargs['title']
    plotdata.append(my_data)
t_datacollection1 = time.time()
print(f'time for data collection: {t_datacollection1 - t_datacollection0}')


#####

dataspec_wiki = [
    {'wiki':'commonswiki'},
    {'wiki':'wikidatawiki'},
    {'wiki':'enwiki'},
    {'wiki':'dewiki'},
    {'wiki':'jawiki'},
    {'wiki':'nlwiki'},
    {'wiki':'fiwiki'},
]

t_datacollection0 = time.time()
plotdata_wiki = []
for kwargs in dataspec_wiki:
    my_data = {}
    my_data['data'] = get_totaledit_count(**kwargs)
    my_data['infotxt'] = kwargs['wiki']
    plotdata_wiki.append(my_data)
t_datacollection1 = time.time()
print(f'time for data collection: {t_datacollection1 - t_datacollection0}')

#############
### Plots ###
#############

import matplotlib.pyplot as plt
import numpy as np

def plot_worker(plotdata, do_ylog=False):
    fig,hax = plt.subplots(1)

    # print(plotdata)

    # latest time in database (FIXME: find from data), think about timezone
    dt_max = datetime.datetime(2025, 11, 6, 16, 0)
    for curr_q in plotdata:
        curr_d = curr_q['data']
        # datatype: datetime.timedelta
        #           v-- earlier events <=> negative value (then they appear on the left of the time axis)
        plot_dt = [ -(dt_max-_['t']) for _ in curr_d ]
        plot_dt = [ _.total_seconds() for _ in plot_dt ]
        plot_v  = [ _['value'] for _ in curr_d ]
        #print(plot_dt)
        #print(plot_v)
        hax.plot(np.array(plot_dt)/3600.0,plot_v,'+--',label=curr_q['infotxt'])
        # break

    hax.set_xlabel(f'time before {dt_max} [hours]')
    hax.set_ylabel('edit count/hour')
    if do_ylog:
        hax.set_yscale('log')
    hax.legend()

    # GROUP BY + aggregate function does not provide zero values for hours w/o any events
    hax.set_title('Edit Counts (gaps in time-series not filled with zeros)')
    plt.show()

plot_worker(plotdata)
# plot_worker(plotdata_wiki, do_ylog=True)
