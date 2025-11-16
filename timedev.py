#!/usr/bin/env python3

# Christoph Lechner, 2025-11-16
# Demo program to study options for measuring execution time with decorators

import datetime
import time
from functools import wraps
from copy import deepcopy

class MyTimer:
    # global variable to measure time
    time_stats = []

    @classmethod
    def timeit(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tnow = datetime.datetime.now()
            tstart = time.perf_counter()
            result = func(*args,**kwargs)
            tend = time.perf_counter()
            print(f'{func.__name__}: {tend-tstart:.6f} seconds')
            self.time_stats.append({'tstart': tnow, 'func': func.__name__, 'dur': (tend-tstart)})
            return result
        return wrapper

    @classmethod
    def report1(self, f):
        """
        Function f is called for every bit of statistical info
        FIXME: Should this also clear the collected statistics?
        """
        sorted_time_stats = sorted(self.time_stats, key=lambda obj: obj['tstart'])
        for curr_stat in sorted_time_stats:
            f(curr_stat)


@MyTimer.timeit
def do_something():
    # do ... important ... work
    time.sleep(2)
    return

@MyTimer.timeit
def do_work():
    # do ... important ... work
    time.sleep(2)
    return

# let's do a few function calls
do_something()
do_work()
do_something()


### process the results ###
def report(s):
    print(s)

print('Collected time stats: ')
MyTimer.report1(report)
