#!/usr/bin/env python3

# Tests for streamreader.
# Most these tests require an Internet connection since the stream reader
# connects to the data source.
#
# Christoph Lechner, 2025-Nov-27

import subprocess
import threading
import time
import os
import signal
from pathlib import Path
import gzip
import json

################################
### TEST REACTION TO SIGNALS ###
################################

signal_tests_sleep=5
signal_tests_list_files=False

def send_signal(pid, *, ignore_process_lookup_error=False, signal=signal.SIGTERM):
    time.sleep(signal_tests_sleep)
    try:
        os.kill(pid, signal)
    except ProcessLookupError as e:
        if ignore_process_lookup_error:
            pass # if we know that the process may not be there (anymore), ignore the error
        else:
            raise e

def send_SIGTERM(pid, *, ignore_process_lookup_error=False):
    send_signal(pid, ignore_process_lookup_error=ignore_process_lookup_error, signal=signal.SIGTERM)
def send_SIGUSR1(pid, *, ignore_process_lookup_error=False):
    send_signal(pid, ignore_process_lookup_error=ignore_process_lookup_error, signal=signal.SIGUSR1)

def run_program(tmp_path):
    # assumes that this test script is the same directory as the program to run
    test_dir = Path(__file__).parent
    path_sr =     test_dir / 'wikistreamreader.py'

    # path_outdir = test_dir / 'scratch_output_dir1/'
    path_outdir = tmp_path

    # os.mkdir(path_outdir)
    p = subprocess.Popen(
        # useful for tests: sleep gives return code -15 (in Python) if SIGTERM is sent
        # ['/bin/sleep', '100'],
        [str(path_sr), '--outdir='+str(path_outdir)],
        cwd=test_dir # CWD = directory where the script lives
        )

    print(p.pid)

    return ({'p':p, 'outdir':path_outdir})


def inspect_outfile(*, fn, do_gzip=True):
    """
    If gzip file was truncated, this code likely throws the exception
    "EOFError: Compressed file ended before the end-of-stream marker was reached"    
    """
    # helper function so we can use "with ... as fin" for both modes
    def open_infile(fn_in):
        print(f'Input file: {fn_in}')
        if do_gzip:
            return gzip.open(fn_in,'r')
        else:
            return open(fn_in,'rb')

    linecntr=0
    bad_jsoncntr=0
    with open_infile(fn) as fin:
        for l_ in fin:
            l_ = l_.decode() # we use file in 'rb' mode now so we can switch transparently between gzip'd and standard files
            linecntr += 1
            #
            try:
                event = json.loads(l_)
            except ValueError:
                bad_jsoncntr+=1
                continue

    print(f'lines={linecntr}, bad_json={bad_jsoncntr}')
    # assert linecntr>=1 # this one would fail, if the server does not send any events at the moment
    assert bad_jsoncntr==0

### First (and most important) test: Check that streamreader reacts to SIGTERM ###
def test_honors_SIGTERM(capsys, tmp_path):
    run = run_program(tmp_path)
    p = run['p']
    path_outdir = run['outdir']

    t = threading.Thread(target=send_SIGTERM, args=(p.pid,))
    t.start()

    # wait for process to finish
    p.wait()
    t.join()

    if signal_tests_list_files:
        with capsys.disabled():
            print(f'\n*** contents of output directory {str(path_outdir)} ***')
            subprocess.run(['/bin/ls', '-ltr', path_outdir])

    rc = p.returncode
    print(f'exit code was {rc}')
    assert rc==0

### Test: Check that streamreader reacts to SIGUSR1 ###
# When the event stream delivers events, there should be at least two
# output files ("at least" because if test is started just before the
# hourly rotation, there may be more output files)
def test_honors_SIGUSR1(capsys, tmp_path):
    run = run_program(tmp_path)
    p = run['p']
    path_outdir = run['outdir']

    # send SIGUSR1
    t = threading.Thread(target=send_SIGUSR1, args=(p.pid,))
    t.start()
    t.join() # waits for delivery of signal

    t = threading.Thread(target=send_SIGTERM, args=(p.pid,))
    t.start()

    # wait for process to finish
    p.wait()
    t.join()

    rc = p.returncode
    print(f'exit code was {rc}')

    if signal_tests_list_files:
        with capsys.disabled():
            print(f'\n*** contents of output directory {str(path_outdir)} ***')
            subprocess.run(['/bin/ls', '-ltr', path_outdir])

    # count files matching expected filename pattern
    lof = list(path_outdir.glob('stream_*.gz.ready'))
    nfiles = len(lof)
    #with capsys.disabled():
    #    print(f'nfiles={nfiles}')

    assert rc==0
    assert nfiles>=2

    ### test that output files are valid .gz format
    with capsys.disabled():
        for fn in lof:
            inspect_outfile(fn=fn)
