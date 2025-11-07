#!/usr/bin/env python3

# Christoph Lechner, Nov 2025

import json
from requests_sse import EventSource
from requests_sse.client import InvalidStatusCodeError
from my_util import FilenameGen
import os
import time
import datetime

# Force rotation after this number of events in file
# As of 2025-Nov, the i"recentchange" gives less than 200000 events per hour (on avg, every event corresponds to about 150 bytes in the file)
max_events_per_file=500000

# directory holding checkpoints
dir_checkpoints = 'streamdata/'

#####

def load_checkpoint():
    # list all files in provided data directory
    checkpoint_candidates=[]
    for fn_ in os.listdir(dir_checkpoints):
        # print(fn_)
        if fn_.startswith('checkpoint_'):
            tmp_path=dir_checkpoints+'/'+fn_
            if os.path.isfile(tmp_path):
                # print(tmp_path)
                checkpoint_candidates.append(tmp_path)

    fn_checkpoint=None
    if len(checkpoint_candidates)==0:
        print('No checkpoint was found!')
        return None

    checkpoint_candidates.sort(reverse=True)
    # print(checkpoint_candidates)
    fn_checkpoint=checkpoint_candidates[0]

    print(f'going to use checkpoint: {fn_checkpoint}')

    with open(fn_checkpoint,'r') as fin:
        cp_status = fin.readline()

    # remark: Not deleting the checkpoint file! Once the first new file is written, the file from which we resumed becomes meaningless anyhow because the youngest checkpoint file is used for any future resume

    return(cp_status)

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


    checkpoint_throttle_cntr=0
    last_checkpoint=None
    # Example for an eventid that worked in 2025-Nov tests (note that it is only valid for a few minutes):
    # last_id='[{"topic":"eqiad.mediawiki.recentchange","partition":0,"offset":-1},{"topic":"codfw.mediawiki.recentchange","partition":0,"timestamp":1762467620155}]'

    # If no checkpoint was found, this returns None (default value of latest_event_id argument to EventSource)
    last_id = load_checkpoint()
    while True:
        try:
            # Note 2025-Nov-07: It could be that providing too old checkpointing infos results in HTTP 400...
            with EventSource(url, latest_event_id=last_id, **kwargs) as stream:
                for event in stream:
                    if event.type == 'message':
                        try:
                            change = json.loads(event.data)
                        except ValueError:
                            continue # next event

                        # Store id of the event just received, allows to resume in case the connection breaks and cannot be restarted immediately by EventSource. This would be the case if the server returns a HTTP 503 status (or any other error code).
                        last_id = event.last_event_id

                        # write checkpoints
                        checkpoint_throttle_cntr+=1
                        if (checkpoint_throttle_cntr>100):
                            checkpoint_data=event.last_event_id
                            last_checkpoint = store_checkpoint(status=last_checkpoint, data=checkpoint_data)
                            checkpoint_throttle_cntr=0

                        # process the *raw* event
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

                        # further processing in user-provided callback function (parsed JSON)
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

def outfile_open(fn):
    # Future improvement: use gzip.open to write data gzip-compressed (JSON can be compressed by factor of about 5)
    fout = open(fn,'w')
    print(f'Opened output file {fn}')
    return(fout)

def outfile_rotate(status):
    fnold = status['fn']
    fnnew = fnold+'.ready'
    print('Closing file '+fnold)
    status['fout'].close()
    os.rename(fnold, fnnew)
    print('Renamed file (to mark as ready for further processing) -> '+fnnew)
    #
    status['fn'] = status['fng'].getfn()
    status['fout'] = outfile_open(status['fn'])
    status['events_in_file']=0

def cb_process_raw(event, status):
    # If needed: file rotation
    if status['fng'].rot_timecrit():
        print('Rotating output file (time crit.)')
        outfile_rotate(status)
    elif status['events_in_file']>=max_events_per_file:
        print('Rotating output file (max events reached)')
        outfile_rotate(status)

    status['fout'].write(event.data)
    status['fout'].write('\n')
    status['events_in_file']+=1


if __name__=="__main__":
    status={}
    status['events_in_file']=0
    status['fng'] = FilenameGen()
    status['fn'] = status['fng'].getfn()
    status['fout'] = outfile_open(status['fn'])

    # lambda captures local dict for status management
    cb_raw = lambda event_: cb_process_raw(event_, status)

    # Download of historical data (WARNING: can generate lots of data).
    # See section "Historical Consumption" in https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service (accessed 2025-Nov-07)
    url_hist = 'https://stream.wikimedia.org/v2/stream/recentchange?since=2025-11-07T00:00:00Z'
    get_stream_data(url=url_hist, cb=cb_demo_user, cb_raw=cb_raw)
