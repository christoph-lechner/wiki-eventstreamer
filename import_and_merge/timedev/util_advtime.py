#!/usr/bin/env python3

# Christoph Lechner, 2025-11-16
# Demo program to study options for measuring execution time with decorators

# online resource: https://realpython.com/primer-on-python-decorators/

import datetime
import time
from functools import wraps
from copy import deepcopy

class MyTimer:
    # global variable to measure time
    time_stats = []

    @classmethod
    def timeit(self, func=None, *, infotxt=None):
        # Case 1: called without parentheses
        # @MyTimer.timeit
        # def f():
        #     ...
        if func:
            return self._make_wrapper(func, infotxt=None)

        # Case 2: called with parentheses
        # @MyTimer.timeit(infotxt='Hallo World')
        # def f():
        #     ...
        def decorator(func):
            return self._make_wrapper(func, infotxt=infotxt)
        return decorator

    @classmethod
    def _make_wrapper(self,func,infotxt):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tnow = datetime.datetime.now()
            tstart = time.perf_counter()
            result = func(*args,**kwargs)
            tend = time.perf_counter()
            print(f'{func.__name__}: {tend-tstart:.6f} seconds')
            self.time_stats.append({'tstart': tnow, 'func': func.__name__, 'dur': (tend-tstart), 'infotxt':infotxt})
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


if __name__=="__main__":
    @MyTimer.timeit
    def do_something():
        # do ... important ... work
        time.sleep(2)
        return

    # !must provide name of the argument here!
    @MyTimer.timeit(infotxt='Hallo')
    def do_work():
        # do ... important ... work
        time.sleep(2)
        return

    # Finally, let's demonstrate that the infotxt passed to the decorator
    # of a sub-function can depend on the argument passed to the function.
    def do_cool_things(arg):
        @MyTimer.timeit(infotxt=arg)
        def f():
            print('... Hello from f ...')
            time.sleep(1)
            return
        f()


    # let's do a few function calls
    do_something()
    do_work()
    do_something()
    do_cool_things('value1')
    do_cool_things('value2')


    ### process the results ###
    def report(s):
        print(s)

    print('Collected time stats: ')
    MyTimer.report1(report)
