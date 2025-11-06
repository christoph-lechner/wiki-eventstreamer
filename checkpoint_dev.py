#!/usr/bin/env python3

import datetime
import time
import os

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

s = store_checkpoint(data='Hallo World')
print(s)
s = store_checkpoint(status=s, data='X Hallo World\nY')

