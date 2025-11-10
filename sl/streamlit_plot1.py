"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import numpy as np
import pandas as pd
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
        SELECT
           DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,
           COUNT(*)
        FROM wiki_change_events_test
        WHERE
           event_type='edit' AND event_wiki=%s AND event_title=%s
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


#############
### Plots ###
#############

def plot_worker(plotdata, do_ylog=False):
    # fig,hax = plt.subplots(1)

    # latest time in database (FIXME: find from data), think about timezone
    dt_max = datetime.datetime(2025, 11, 9, 19, 0)
    # for curr_q in plotdata:
    curr_d = plotdata['data']
    # datatype: datetime.timedelta
    #           v-- earlier events <=> negative value (then they appear on the left of the time axis)
    plot_dt = [ -(dt_max-_['t']) for _ in curr_d ]
    plot_dt = [ _.total_seconds() for _ in plot_dt ]
    plot_v  = [ _['value'] for _ in curr_d ]
    #print(plot_dt)
    #print(plot_v)
    plot_x = np.array(plot_dt)/3600.0
    plot_y = np.array(plot_v)

    # GROUP BY + aggregate function does not provide zero values for hours w/o any events
    #hax.set_title('Edit Counts (gaps in time-series not filled with zeros)')
    #plt.show()
    return plot_x,plot_y



import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np

print(
"""
# example code from
# https://discuss.streamlit.io/t/plot-multiple-line-chart-in-a-single-line-chart/66339/4

date_range = pd.date_range(start="2023-01-01", end="2023-12-31", freq='M')
data = date_range.month + np.random.normal(0, 1, size=len(date_range))
data_green_line = np.linspace(start=20, stop=10, num=len(date_range)) + np.random.normal(0, 1, size=len(date_range))
split_index = len(data) // 2

trace_blue = go.Scatter(x=date_range[:split_index], y=data[:split_index], mode='lines', name='Blue Part', line=dict(color='blue'))
trace_red = go.Scatter(x=date_range[split_index-1:], y=data[split_index-1:], mode='lines', name='Red Part', line=dict(color='red'))
trace_green = go.Scatter(x=date_range, y=data_green_line, mode='lines', name='Green Line', line=dict(color='green'))

data_combined = [trace_blue, trace_red, trace_green]

layout = go.Layout(title='Combined Chart with Blue-Red Transition and Green Line',
                   xaxis=dict(title='Date'),
                   yaxis=dict(title='Data Value'),
                   hovermode='closest')

fig_combined = go.Figure(data=data_combined, layout=layout)

st.plotly_chart(fig_combined)

print('***')
print(type(data_green_line))
print(date_range)
print(data_combined)
""")

###

# https://matplotlib.org/stable/gallery/color/color_cycle_default.html
#import matplotlib.pyplot as plt
#prop_cycle = plt.rcParams['axes.prop_cycle']
#print(prop_cycle)
plt_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

import itertools
iter_color = itertools.cycle(plt_colors)


traces = []
for qq in plotdata:
    plot_x,plot_y = plot_worker(qq)
    # new_trace = go.Scatter(x=plot_x, y=plot_y, mode='lines', name=qq['infotxt'], line=dict(color='blue'))
    new_trace = go.Scatter(x=plot_x, y=plot_y, mode='lines', name=qq['infotxt'], line=dict( color=next(iter_color) ))
    traces.append(new_trace)

layout = go.Layout(
    title='Events per Hour (TODO: Fill Gaps in DB Output with Zeros)',
    xaxis=dict(title='Hours Before Nov 9, 20:00'),
    yaxis=dict(title='Edits / hour'),
    hovermode='closest',
)

fig_combined = go.Figure(data=traces, layout=layout)

st.plotly_chart(fig_combined)
