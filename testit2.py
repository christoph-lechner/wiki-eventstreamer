#!/usr/bin/env python3

# CL, 2025-11-05:
# installed packages
# Successfully installed certifi-2025.10.5 charset_normalizer-3.4.4 idna-3.11 requests-2.32.5 requests_sse-0.5.2 urllib3-2.5.0


# from https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service

import json
from requests_sse import EventSource
from requests_sse.client import InvalidStatusCodeError
from my_util import FilenameGen
import os
import time
import datetime

dir_checkpoints = 'streamdata/'


def store_checkpoint(*, status=None, data):
    """
    No need to provide 'status' when it is the first checkpoint.
    For following calls, provide data returned from previous call.
    """
    outstatus = {}
    tnow = datetime.datetime.now()
    fnnew = dir_checkpoints+'/checkpoint_' + tnow.strftime('%Y%m%dT%H%M%S.%f')
    with open(fnnew,'w') as fout:
        fout.write(data)

    if status:
        if 'checkpoint_file' in status:
            fnold = status['checkpoint_file']
            # in very unlikely scenario (calls at very frequency), the filenames can be identical
            if fnnew==fnold:
                print('Warning: checkpoint filenames identical (old checkpoint file was overwritten, which is not perfect as it could cause loss of checkpointing info in case of crash) -> not deleting')
            else:
                try:
                    os.unlink(fnold)
                except FileNotFoundError:
                    pass # ignore FileNotFoundError: failing to delete old checkout should not crash entire program. When resuming from checkpoint, the freshest file is used (based on date/time in filename).

    outstatus['checkpoint_dt']   = tnow
    outstatus['checkpoint_file'] = fnnew
    return(outstatus)

def get_stream_data(url = 'https://stream.wikimedia.org/v2/stream/recentchange', cb=None, cb_raw=None):
    # Info: Wikipedia blocks Python scripts -> gives 403
    # Fake Firefox -> gives 200
    kwargs = dict()
    kwargs['headers'] = dict()
    kwargs['headers']['User-Agent']='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    #
    # FIXME: add code to obtain event id info from checkpoint file
    checkpoint_throttle_cntr=0
    last_checkpoint=None
    last_id = None
    while True:
        try:
            with EventSource(url,**kwargs) as stream:
                for event in stream:
                    if event.type == 'message':
                        try:
                            change = json.loads(event.data)
                        except ValueError:
                            continue # next event

                        # write checkpoints
                        checkpoint_throttle_cntr+=1
                        if (checkpoint_throttle_cntr>100):
                            checkpoint_throttle_cntr=0
                            # FIXME: is 'id' the correct element in the decoded JSON?
                            if 'id' in change:
                                checkpoint_data=str(change['id'])
                                last_checkpoint = store_checkpoint(status=last_checkpoint, data=checkpoint_data)
                            else:
                                print('warning: not storing checkpoint because field id is missing')

                        # this prints the *raw* data
                        if cb_raw is not None:
                            cb_raw(event)
                        """
                        In very rare cases, expected fields may be missing from the parsed JSON data. On 2025-Nov-05, this script was crashing after a few hours and more than 300000 processed messages with the following exception (crash was reproducible):
                        Traceback (most recent call last):
                          File "/home/cl/work/wikitest/./testit.py", line 34, in <module>
                            if change['user'] == 'Yourname':
                        KeyError: 'user'
                        """
                        # discard canary events
                        if 'meta' in change:
                            if 'domain' in change['meta']:
                                if change['meta']['domain'] == 'canary':
                                    continue

                        # further processing in user-provided callback function
                        if cb is not None:
                            cb(change)
        except InvalidStatusCodeError as e:
            print(f'EventSource: HTTP status code: {e.status_code}. Retrying...')
            time.sleep(5)

#################
### MAIN CODE ###
#################

def cb_demo_user(change):
    # print(change)
    if 'user' in change:
        if change['user'] == 'Yourname':
            print('special username detected')
            print(change)
            last_id = event.last_event_id
            print(last_id)

def open_outfile(fn):
    fout = open(fn,'w')
    print(f'Opened output file {fn}')
    return(fout)

def cb_process_raw(event, status):
    if status['fng'].qq():
        fnold = status['fn']
        fnnew = fnold+'.ready'
        print('Closing file '+fnold)
        status['fout'].close()
        os.rename(fnold, fnnew)
        print('Renamed file (to mark as ready for further processing) -> '+fnnew)
        #
        status['fn'] = status['fng'].getfn()
        status['fout'] = open_outfile(status['fn'])

    status['fout'].write(event.data)
    status['fout'].write('\n')


if __name__=="__main__":
    status={}
    status['fng'] = FilenameGen()
    status['fn'] = status['fng'].getfn()
    status['fout'] = open_outfile(status['fn'])

    # lambda captures local dict for status management
    cb_raw = lambda event_: cb_process_raw(event_, status)

    get_stream_data(cb=cb_demo_user, cb_raw=cb_raw)

# - Run this Python script.
# - Publish an edit to [[Sandbox]] on test.wikipedia.org, and observe it getting printed.
# - Quit the Python process.
# - Pass last_id to last_event_id parameter when creating the stream like
#   with EventSource(url,  latest_event_id=last_id) as stream: ...
# - Publish another edit, while the Python process remains off.
# - Run this Python script again, and notice it finding and printing the missed edit.
