# README

This directory contains a maintenance script for the machine running the `streamreader`.
Based on the user-provided maximum age, the script removes old files, thus curbing the total disk space consumed by the files containing stream dumps.
The script is to be set up as cronjob running (for instance at midnight) as the user holding the data files.


The tool inspects all files in the data directory (without recursive search) and only considers files having the format `stream_YYYYmmddTHHMMSS_NNNNNN.gz.ready` (here `YYYYmmddTHHMMSS` is date/time in ISO format, `NNNNNN` is a sequence number). Files with names not matching this format are ignored. The age of the file is computed based on the time difference between the current time and the timestamp extracted from the filename.

## Running it
```
./remove_old_streamdumps.py [--dir=/data/directory] [--max-age-in-days=<value>] [--delete]
```
* The data directory is specified using parameter `--dir`. The default value is given in the code.
* The argument `--max-age-in-days` can be used to specify when old data files are to be deleted. Default value is 28 days.
* Specify the argument `--delete` to actually delete old files (if not specified the tool reports what it would do)

The program does not need any special Python packages.
