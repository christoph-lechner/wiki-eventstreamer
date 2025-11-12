#!/usr/bin/env python3

import psycopg
import json
import datetime
import time
from db_query import get_totaledit_count, get_edit_count
from db_conn import get_db_conn

###########################
### Obtain data from DB ###
###########################

conn = get_db_conn()

# https://www.psycopg.org/psycopg3/docs/advanced/rows.html#row-factories
from psycopg.rows import dict_row
cur = conn.cursor(row_factory=dict_row)


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
#dataspec = [
#    {'wiki':'dewiki', 'title':'Wolfgang Amadeus Mozart'},
#]


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
    my_data['data'] = get_totaledit_count(cur, **kwargs)
    my_data['infotxt'] = kwargs['wiki']
    plotdata_wiki.append(my_data)
t_datacollection1 = time.time()
print(f'time for data collection: {t_datacollection1 - t_datacollection0}')

#############
### Plots ###
#############
def prepare_counts_for_plot(curr_d, t0):
    # datatype: datetime.timedelta
    #           v-- earlier events <=> negative value (then they appear on the left of the time axis)
    plot_dt = [ -(t0-_['t']) for _ in curr_d ]
    plot_dt = [ _.total_seconds() for _ in plot_dt ]
    plot_v  = [ _['value'] for _ in curr_d ]
    return plot_dt,plot_v

import matplotlib.pyplot as plt
import numpy as np

# latest time in database (FIXME: find from data), think about timezone
dt_max = datetime.datetime(2025, 11, 9, 19, 0)
def plot_worker(plotdata, do_ylog=False):
    fig,hax = plt.subplots(1)

    # print(plotdata)

    for curr_q in plotdata:
        (plot_dt,plot_v) = prepare_counts_for_plot(curr_q['data'], t0=dt_max)
        hax.plot(np.array(plot_dt)/3600.0,np.array(plot_v),'+--',label=curr_q['infotxt'])

    hax.set_xlabel(f'time before {dt_max} [hours]')
    hax.set_ylabel('edit count/hour')
    if do_ylog:
        hax.set_yscale('log')
    hax.legend()

    # GROUP BY + aggregate function does not provide zero values for hours w/o any events
    hax.set_title('Edit Counts (gaps in time-series not filled with zeros)')
    plt.show()

# print(plotdata)
plot_worker(plotdata)
plot_worker(plotdata_wiki, do_ylog=True)
