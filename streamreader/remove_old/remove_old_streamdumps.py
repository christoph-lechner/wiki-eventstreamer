#!/usr/bin/env python3

# C. Lechner, 2025-Dec-14

# One issue is that the filenames do not tell us the timezone.
# - If this script is running on the same machine this is not an issue.
# - Furthermore, as data retention times are about 14 days typically, so even an offset of a several hours (if acquisition machine runs with UTC and machine running this script runs in local time) does not completely trash our data

from pathlib import Path
import os
import re
from dataclasses import dataclass
import datetime
import argparse

# defaults
DATADIR = Path('/srv/wikidata/in/')
MAX_AGE_IN_DAYS_DEFAULT = 28




@dataclass
class FileInfo:
    is_valid_filename: bool = False
    fn: str = None
    ts: datetime.datetime = None

def parsefn(fn):
    m = re.match(r'^stream_([0-9]{8}T[0-9]{6})_[0-9]+.gz.ready$', fn)
    if m:
        ts_str = m.group(1) # first parenthesized subgroup
        # print(f'match: {ts_str}')
        ts = datetime.datetime.fromisoformat(ts_str)
        return FileInfo(is_valid_filename=True,fn=fn,ts=ts)
    return FileInfo(is_valid_filename=False,fn=fn)

def can_expire(fn, *, max_age_in_days=MAX_AGE_IN_DAYS_DEFAULT):
    fi = parsefn(fn)
    if not fi.is_valid_filename:
        return False # do NOT delete: not a file with streamdump, or could not parse filename

    # is file with streamdump, let's check the date
    tnow = datetime.datetime.now()
    deltat = tnow - fi.ts
    age_in_days = deltat.total_seconds()/(24*3600)
    return (age_in_days>max_age_in_days)


#####################
##### MAIN CODE #####
#####################
def file_action_report(fullpath:Path):
    print(f'reporting: too old file {str(fullpath)}')

def file_action_del(fullpath:Path):
    print(f'to be implemented: del action for {str(fullpath)}')

def main(*,datadir=None, old_file_action=None, max_age_in_days=MAX_AGE_IN_DAYS_DEFAULT):
    if datadir is None:
        raise ValueError('please specify datadir')
    if old_file_action is None:
        old_file_action=file_action_report

    if not callable(old_file_action):
        raise ValueError('old_file_action parameters not callable')

    # check all files in data directory (un-sorted processing order!)
    list_delete=[]
    for fn_ in os.listdir(datadir):
        if can_expire(fn_, max_age_in_days=max_age_in_days):
            list_delete.append(fn_)

    list_delete.sort()

    for fn_ in list_delete:
        fullpath = datadir / fn_
        old_file_action(fullpath)



if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='data directory to process', default=DATADIR)
    parser.add_argument('--max-age-in-days', type=int, help='maximum age of files to keep', default=MAX_AGE_IN_DAYS_DEFAULT)
    parser.add_argument('--delete', action='store_true', default=False)
    args = parser.parse_args()
    # print(args)


    # Based on user input, set up function for action
    # Only if *explicitly* requested by user, files will be deleted,
    # otherwise a report will be generated what would be done
    action=file_action_report
    if args.delete:
        action=file_action_del

    max_age=args.max_age_in_days
    if max_age<=0:
        raise ValueError('maximum file age has to be positive')
    if max_age<3:
        raise ValueError('currently this script does not permit a max. file age below 3 days')

    main(datadir=Path(args.dir), old_file_action=action, max_age_in_days=max_age)
