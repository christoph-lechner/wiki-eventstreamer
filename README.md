# README
Christoph Lechner, Nov 2025

## Setup/Preparation
Clone the git repository.

Optional: Set up a new Python virtual environment.

Install Python packages for wiki streamreader:
```
pip install -r requirements.txt
```

## Running it
The simplest way to run it is to execute
```
./wikistreamreader.py
```
Output goes to the directory `streamdata/`.

After it has been running for several hours, the data directory might look like this:
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
The files with extension `.ready` will not be touched by the reader anymore, so they are ready for pickup for further processing.

In case the program is restarted, the `checkpoint_*` file contains information to resume the streaming. Note that this is only possible if the interruption was not longer than a few minutes. These checkpoint files are replaced every few seconds and only the newest one (using timestamp in filename) will be used.
