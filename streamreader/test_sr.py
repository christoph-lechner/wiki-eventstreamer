#!/usr/bin/env python3

import subprocess
import threading
import time
import os
import signal
from pathlib import Path


### First test: Check that streamreader reacts to SIGTERM ###
def test_honors_SIGTERM(capsys, tmp_path):
    def send_SIGTERM(pid, ignore_process_lookup_error=True):
        time.sleep(5)
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError as e:
            if ignore_process_lookup_error:
                pass # if we know that the process may not be there (anymore), ignore the error
            else:
                raise e

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

    t = threading.Thread(target=send_SIGTERM, args=(p.pid,))
    t.start()

    # wait for process to finish
    p.wait()
    t.join()

    with capsys.disabled():
        print(f'\n*** contents of output directory {str(path_outdir)} ***')
        subprocess.run(['/bin/ls', '-ltr', path_outdir])

    rc = p.returncode
    print(f'exit code was {rc}')
    assert rc==0

