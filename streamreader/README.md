# README
## Introduction
According to the [description](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service) the HTTPS connection is reset after about 15 minutes. Therefore a special client is required.

See the [description of the EventStreams HTTP Service at wikimedia.org](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service) for more (technical) details.

## Preparations
Ideally a dedicated user account is used to run this program, but this is not necessary.

For running the program `wikistreamreader.py` a dedicated user account is prepared. Password-based login is disabled by purpose and ssh-public-key login is also not available.
The specifics are described [here](config_permissions.md).

## Setup/Preparation
Optional: Set up a new Python virtual environment.

Install Python packages for wiki streamreader:
```
pip install -r requirements.txt
```

## Running it
### For Production: Running using systemctl
The advantage of using `systemd` is that the program is launched at system start up and is automatically restarted in the unlikely case of a crash.
For a few notes taken while setting up my installation, see [here](config_systemctl.md).

### For Testing: Running on the Command Line
The simplest way to run it is to execute
```
./wikistreamreader.py
```
Output goes into a directory that is to be configured at the beginning of the script.

After the script has been running for several hours, the data directory might look like this:
```
cl@ubuntu:~/wikireader/wiki-eventstreamer/streamdata$ ls -l
total 1698868
-rw-rw-r-- 1 cl cl       163 Nov  7 10:52 checkpoint_20251107T105213.513064
-rw-rw-r-- 1 cl cl 106048192 Nov  7 00:05 stream_20251106T231621_000000001.ready
-rw-rw-r-- 1 cl cl 117611566 Nov  7 01:05 stream_20251107T000500_000000002.ready
-rw-rw-r-- 1 cl cl 136939282 Nov  7 02:04 stream_20251107T010500_000000003.ready
-rw-rw-r-- 1 cl cl 130005728 Nov  7 03:05 stream_20251107T020500_000000004.ready
-rw-rw-r-- 1 cl cl 138086810 Nov  7 04:05 stream_20251107T030500_000000005.ready
-rw-rw-r-- 1 cl cl 138182963 Nov  7 05:05 stream_20251107T040500_000000006.ready
-rw-rw-r-- 1 cl cl 141022158 Nov  7 06:05 stream_20251107T050500_000000007.ready
-rw-rw-r-- 1 cl cl 149044131 Nov  7 07:05 stream_20251107T060500_000000008.ready
-rw-rw-r-- 1 cl cl 171752540 Nov  7 08:05 stream_20251107T070500_000000009.ready
-rw-rw-r-- 1 cl cl 176072155 Nov  7 09:05 stream_20251107T080500_000000010.ready
-rw-rw-r-- 1 cl cl 184411758 Nov  7 10:05 stream_20251107T090500_000000011.ready
-rw-rw-r-- 1 cl cl 150410965 Nov  7 10:52 stream_20251107T100500_000000012
cl@ubuntu:~/wikireader/wiki-eventstreamer/streamdata$
```

### Output File Rotation
There are several reasons for the program to rotate the output file.

* At minute 5 of every hour, the files are rotated.
* After receiving 500000 events, the file will be rotated. This keeps the file size at a manageable level.
* Rotation can also be triggered by sending SIGUSR1 signal

In any case, the following events are written in a new file and the previous file gets the additional extension `.ready`.
These files with extension `.ready` will not be touched by the reader anymore, so they are ready to be collected for further processing.

### Checkpointing
In case the program is restarted, the `checkpoint_*` file contains information to resume the streaming. Note that this is only possible if the interruption was not longer than a few minutes. These checkpoint files are replaced every few seconds and only the newest one (using timestamp in filename) will be used.


### Signals
(Signal handling was implemented on 2025-Nov-10.)

* SIGTERM results in output file being closed (checkpoint file is **not** removed). For instance, this signal is sent by `systemd` when the system is being rebooted.
* SIGUSR1 triggers output file rotation

#### Signal `SIGUSR1` triggers output file rotation
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
