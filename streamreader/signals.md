# Signals
Signal handling was implemented on 2025-Nov-10.

* SIGTERM results in output file being closed (checkpoint file is **not** removed). This signal is sent by systemd when the system is being rebooted.
* SIGUSR1 triggers output file rotation

## Signal `SIGUSR1` triggers output file rotation
Before:
```
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ ls -l streamdata/
total 2000
-rw-r--r-- 1 dataacq dataacq     163 Nov 10 20:26 checkpoint_20251110T202645.046384
-rw-r--r-- 1 dataacq dataacq 2036606 Nov 10 20:26 stream_20251110T202245_000001.gz
drwxrwxr-x 3 dataacq dataacq    4096 Nov 10 20:14 u
```
After `SIGUSR1` was sent to the process:
```
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ ls -l streamdata/
total 2264
-rw-r--r-- 1 dataacq dataacq     163 Nov 10 20:27 checkpoint_20251110T202712.137326
-rw-r--r-- 1 dataacq dataacq 2283636 Nov 10 20:27 stream_20251110T202245_000001.gz.ready
-rw-r--r-- 1 dataacq dataacq   21667 Nov 10 20:27 stream_20251110T202710_000002.gz
drwxrwxr-x 3 dataacq dataacq    4096 Nov 10 20:14 u
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$
```
