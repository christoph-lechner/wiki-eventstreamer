CL, 2025-11-08

In directory containing `.ready` files that are to be loaded:
```
find streamdata -iname '*.ready' -print | sort > LOF
```

```
$ script -f log_20250811T2030.txt
Script started, output log file is 'log_20250811T2030.txt'.
$ source /home/[redacted]/venv_ws/bin/activate

(venv_ws) $ cat LOF | xargs -n 1 ../import_and_merge/simple_import.py -z
Input file: streamdata/stream_20251107T134442_000000001.gz.ready
.....
Loaded 500000 events
adding hashes to rows ...
deduplicate staged rows bashed on hashes (sometimes the same event is sent multiple times) ...
execute MERGE command (only events with new MD5 hash get stored)
DONE: 500000/500000 rows from file got merged into data table
   breakdown: from file: 500000; after dedupl. 500000; rows merged 500000
Input file: streamdata/stream_20251107T134738_000000002.gz.ready
.....
Loaded 500000 events
adding hashes to rows ...
deduplicate staged rows bashed on hashes (sometimes the same event is sent multiple times) ...
execute MERGE command (only events with new MD5 hash get stored)
DONE: 500000/500000 rows from file got merged into data table
   breakdown: from file: 500000; after dedupl. 500000; rows merged 500000
Input file: streamdata/stream_20251107T134927_000000003.gz.ready
[..]
```
