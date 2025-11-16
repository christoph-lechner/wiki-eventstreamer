#!/usr/bin/env python3

# Christoph Lechner, 2025-11-16
# Demo program to study options for measuring execution time with decorators

import datetime
import time
from functools import wraps

# global variable to measure time
time_stats = []

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tnow = datetime.datetime.now()
        tstart = time.perf_counter()
        result = func(*args,**kwargs)
        tend = time.perf_counter()
        print(f'{func.__name__}: {tend-tstart:.6f} seconds')
        time_stats.append({'tstart': tnow, 'func': func.__name__, 'dur': (tend-tstart)})
        return result
    return wrapper

@timeit
def do_something():
    # do ... important ... work
    time.sleep(2)
    return

@timeit
def do_work():
    # do ... important ... work
    time.sleep(2)
    return

# let's do a few function calls
do_something()
do_work()
do_something()

print('Collected time stats: ')
print(time_stats)
