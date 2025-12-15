# C. Lechner, 2025-12-14

import datetime
import subprocess
from remove_old_streamdumps import parsefn,can_expire,main

AGE_FOR_TEST = 14 # days

def test_filename_match():
    """
    Test that the filenames are correctly matched
    and that timestamp is properly extracted from filename
    -> correct extraction of timestamps is the foundation for all operations
    """
    # properly formated filename
    qq = parsefn('stream_20251213T180500_000067.gz.ready')
    assert qq.is_valid_filename==True
    # check that timestamp is correctly extracted from filename
    ts_expected = datetime.datetime(2025,12,13,18,5,0)
    assert qq.ts==ts_expected

def test_badfilenames():
    # some ill-formatted filenames that should not match
    bad_filenames = [
        # no .ready
        'stream_20251213T180500_000067.gz',
        # wrong prefix
        'streamx_20251213T180500_000067.gz.ready',
        'xstream_20251213T180500_000067.gz.ready',
        'strea_20251213T180500_000067.gz.ready',
        # extra chars
        'stream_20251213T180500_000067.gz.readyX',
        'stream_20251213T180500_000067.Xgz.ready',
        # malformatted timestamp
        'stream_20251213T1805000_000067.gz.ready',
        'stream_20251213T18050_000067.gz.ready',
        'stream_202512130T180500_000067.gz.ready',
        'stream_2025121T180500_000067.gz.ready',
    ]
    for fn_ in bad_filenames:
        qq = parsefn(fn_)
        assert qq.is_valid_filename==False


def test_expiration_logic():
    """
    Test that the expiration logic is working.
    Obviously the most critical part of the entire program.
    """
    def make_filename(ts: datetime.datetime):
        return 'stream_' + ts.strftime('%Y%m%dT%H%M%S') + '_000067.gz.ready'

    tnow = datetime.datetime.now()

    t_nottooold = tnow - datetime.timedelta(days=AGE_FOR_TEST, minutes=-1) # using 1 minute to be not too sensitive to any short stalls when running this test
    assert can_expire(make_filename(t_nottooold), max_age_in_days=AGE_FOR_TEST)==False

    t_old = tnow - datetime.timedelta(days=AGE_FOR_TEST, minutes=1)
    assert can_expire(make_filename(t_old), max_age_in_days=AGE_FOR_TEST) == True


def test_complete_program(tmp_path, capsys):
    """
    Produce fake data directory (with file "age" around the expiration threshold)
    """
    def make_filename(ts: datetime.datetime):
        return 'stream_' + ts.strftime('%Y%m%dT%H%M%S') + '_000067.gz.ready'
    def produce_dummy_file(tmp_path, ts):
        fn = tmp_path / make_filename(ts)
        p = subprocess.run(['/usr/bin/env', 'touch', str(fn)])
        rc = p.returncode
        assert rc==0
        return fn # needed for testing


    tnow = datetime.datetime.now()
    t_nottooold = tnow - datetime.timedelta(days=AGE_FOR_TEST, hours=-1)
    t_old       = tnow - datetime.timedelta(days=AGE_FOR_TEST, hours=1)

    fn_old = produce_dummy_file(tmp_path,t_old)
    produce_dummy_file(tmp_path,t_nottooold)


    def my_action(fn, runs):
        # Action functions must be called *only* for the older file
        assert fn==fn_old

        # ... but this is not sufficient: we need to verify that the
        # function was actually called
        # -> remember arguments of calls here, then on top level check
        # that array is not empty.
        # The combination of assertion passed and array not empty means everything's ok
        runs.append(fn)

    action_function_runs=[]
    main(datadir=tmp_path, old_file_action=lambda fn: my_action(fn,action_function_runs), max_age_in_days=AGE_FOR_TEST)

    # check that function was called
    assert len(action_function_runs)>0
