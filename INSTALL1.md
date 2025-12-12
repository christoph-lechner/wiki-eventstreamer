# Installation: Data Collection
**Remark 2025-Dec: Currently, implementation of automatic removal of very old files with streamdumps is still pending.**

Virtual machine configured with
* 2GB RAM
* 30GB disk (in the setup process, 20GB for `/`, 2GB for `/boot`)
* installation with default configuration "Ubuntu Server"
* install openssh server

Install needed packages
```
cl@wikiacq:~$ sudo apt-get install python3-venv
```

## Creating the Users
For automatic preparation, a script was prepared. This script executes the manual user account configuration from my [notes](https://github.com/christoph-lechner/wiki-eventstreamer/blob/82404aa5568c42a418332d222f80c50cf733552d/streamreader/config_permissions.md). Use at your own risk. The name of the script is `setup-01.sh`.

These are the accounts that were created.
```
cl@wikiacq:~$ id dataacq
uid=1001(dataacq) gid=1001(dataacq) groups=1001(dataacq),1003(wikidata)
cl@wikiacq:~$ id dataxfer
uid=1002(dataxfer) gid=1002(dataxfer) groups=1002(dataxfer),1003(wikidata)
```
Note the extra group `wikidata`. Users needing read-only access to the gathered stream dumps are members of this group, so one could also add the non-privileged user of the admins to this group.

## Preparation of Data Directory
Having created the user accounts, we can prepare the directory that will be used for data storage.
```
cl@wikiacq:~$ sudo mkdir -p /srv/wikiproj/streamdata_in/
cl@wikiacq:~$ sudo chown dataacq:wikidata /srv/wikiproj/streamdata_in/
cl@wikiacq:~$ sudo chmod 750 /srv/wikiproj/streamdata_in/
cl@wikiacq:~$ ls -ld /srv/wikiproj/streamdata_in/
drwxr-x--- 2 dataacq wikidata 4096 Dec 10 23:43 /srv/wikiproj/streamdata_in/
cl@wikiacq:~$
```

## Deployment of Software
Switch user ids (remember, `dataacq` cannot log in)
```
cl@wikiacq:~$ sudo -i
root@wikiacq:~# su - dataacq
```
To have a stable and reproducible software configuration, a dedicated Python virtual environment is prepared:
```
dataacq@wikiacq:~$ mkdir venv_wikistreamreader_prod
dataacq@wikiacq:~$ python3 -m venv venv_wikistreamreader_prod
dataacq@wikiacq:~$ source /home/dataacq/venv_wikistreamreader_prod/bin/activate
```

For future versions, a docker-based solution is being considered. This can be expected to greatly simplify the deployment process.
At the time of this writing, the deployment is done by cloning the git repository.
```
(venv_wikistreamreader_prod) dataacq@wikiacq:~$ mkdir wiki
(venv_wikistreamreader_prod) dataacq@wikiacq:~$ cd wiki
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki$ git clone https://github.com/christoph-lechner/wiki-eventstreamer.git
Cloning into 'wiki-eventstreamer'...
remote: Enumerating objects: 934, done.
remote: Counting objects: 100% (85/85), done.
remote: Compressing objects: 100% (63/63), done.
remote: Total 934 (delta 33), reused 64 (delta 22), pack-reused 849 (from 1)
Receiving objects: 100% (934/934), 1.95 MiB | 6.12 MiB/s, done.
Resolving deltas: 100% (526/526), done.
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki$ cd wiki-eventstreamer/
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki/wiki-eventstreamer$ cd streamreader
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$ pip3 install --upgrade pip
Requirement already satisfied: pip in /home/dataacq/venv_wikistreamreader_prod/lib/python3.12/site-packages (24.0)
Collecting pip
  Downloading pip-25.3-py3-none-any.whl.metadata (4.7 kB)
Downloading pip-25.3-py3-none-any.whl (1.8 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 6.1 MB/s eta 0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.0
    Uninstalling pip-24.0:
      Successfully uninstalled pip-24.0
Successfully installed pip-25.3
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$ pip3 install -r requirements.txt
[..]
Installing collected packages: urllib3, typing-extensions, idna, h11, click, charset_normalizer, certifi, annotated-types, annotated-doc, uvicorn, typing-inspection, requests, pydantic-core, anyio, starlette, requests-sse, pydantic, fastapi
Successfully installed annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.12.0 certifi-2025.11.12 charset_normalizer-3.4.4 click-8.3.1 fastapi-0.124.2 h11-0.16.0 idna-3.11 pydantic-2.12.5 pydantic-core-2.41.5 requests-2.32.5 requests-sse-0.5.2 starlette-0.50.0 typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.6.1 uvicorn-0.38.0
```

### First Manual Test
For this test, we deactivate the virtual environment that was just prepared.
```
(venv_wikistreamreader_prod) dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$ deactivate
```

We run the script that will later be launched by `systemd`. The script activates the virtual environment and then starts the stream dumper. We press `<Ctrl>-<C>` to stop.
```
dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$ ./run_wikistreamreader.sh 
git commit id:
25d35f78804c9c9a62dcb2d770028d46df4879ac

[..]

+ ./wikistreamreader.py --status_port=9090

Opened output file /srv/wikiproj/streamdata_in/stream_20251211T000202_000001.gz
No checkpoint was found!
INFO:     Started server process [2895]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9090 (Press CTRL+C to quit)
^Cgot SIGTERM/SIGINT -> stopping: closing output file, not deleting checkpoint file so we can resume
Closing file /srv/wikiproj/streamdata_in/stream_20251211T000202_000001.gz
Renamed file (to mark as ready for further processing) -> /srv/wikiproj/streamdata_in/stream_20251211T000202_000001.gz.ready
stopping
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [2895]
dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$
```

Let's have a look into the output directory to see if data was written:
```
dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$ ls -l /srv/wikiproj/streamdata_in/
total 128
-rw-rw-r-- 1 dataacq dataacq    149 Dec 11 00:02 checkpoint_20251211T000224.077804
-rw-rw-r-- 1 dataacq dataacq 124651 Dec 11 00:02 stream_20251211T000202_000001.gz.ready
dataacq@wikiacq:~/wiki/wiki-eventstreamer/streamreader$
```
**OK, this looks good.**

Finally, the two files are deleted (*manual manipulation of files in the data directory should be the absolute exception and one should work very careful and think twice before issuing any commands*):
```
dataacq@wikiacq:~$ rm /srv/wikiproj/streamdata_in/checkpoint_20251211T000224.077804 /srv/wikiproj/streamdata_in/stream_20251211T000202_000001.gz.ready
```

### Setup of the service
Copy the file `wikistreamreader.service` to `/etc/systemd/system/`:
```
cl@wikiacq:~$ sudo cp /home/dataacq/wiki/wiki-eventstreamer/streamreader/wikistreamreader.service /etc/systemd/system/
```

Then: first enable the service (after re-reading the configuration files), secondly start the service:
```
cl@wikiacq:~$ sudo systemctl daemon-reload
cl@wikiacq:~$ sudo systemctl enable wikistreamreader
Created symlink /etc/systemd/system/multi-user.target.wants/wikistreamreader.service → /etc/systemd/system/wikistreamreader.service.
cl@wikiacq:~$ sudo systemctl start wikistreamreader
```

Let's check the status:
```
cl@wikiacq:~$ sudo systemctl status wikistreamreader
● wikistreamreader.service - CL's wiki stream reader
     Loaded: loaded (/etc/systemd/system/wikistreamreader.service; enabled; preset: enabled)
     Active: active (running) since Thu 2025-12-11 00:16:23 UTC; 55s ago
   Main PID: 3031 (run_wikistreamr)
      Tasks: 3 (limit: 2267)
     Memory: 37.1M (peak: 37.6M)
        CPU: 1.060s
     CGroup: /system.slice/wikistreamreader.service
             ├─3031 /bin/bash /home/dataacq/wiki/wiki-eventstreamer/streamreader/run_wikistreamreader.sh
             └─3033 python3 ./wikistreamreader.py --status_port=9090

Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3031]: ++ VIRTUAL_ENV_PROMPT='(venv_wikistreamreader_prod) '
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3031]: ++ export VIRTUAL_ENV_PROMPT
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3031]: ++ hash -r
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3031]: + ./wikistreamreader.py --status_port=9090
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: Opened output file /srv/wikiproj/streamdata_in/stream_20251211T001623_000001.gz
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: No checkpoint was found!
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: INFO:     Started server process [3033]
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: INFO:     Waiting for application startup.
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: INFO:     Application startup complete.
Dec 11 00:16:23 wikiacq run_wikistreamreader.sh[3033]: INFO:     Uvicorn running on http://0.0.0.0:9090 (Press CTRL+C to quit)
cl@wikiacq:~$
```

We can verify that data collection is working by taking a look into the storage directory:
```
cl@wikiacq:~$ sudo ls -l /srv/wikiproj/streamdata_in/
total 600
-rw-r--r-- 1 dataacq dataacq    149 Dec 11 00:18 checkpoint_20251211T001802.973673
-rw-r--r-- 1 dataacq dataacq 609956 Dec 11 00:18 stream_20251211T001623_000001.gz
cl@wikiacq:~$
```

Restart the system, to check that everything comes back after reboot.
After the reboot:
```
cl@wikiacq:~$ sudo ls -l /srv/wikiproj/streamdata_in/
total 1372
-rw-r--r-- 1 dataacq dataacq     163 Dec 11 00:19 checkpoint_20251211T001949.408178
-rw-r--r-- 1 dataacq dataacq     163 Dec 11 00:20 checkpoint_20251211T002014.994795
-rw-r--r-- 1 dataacq dataacq 1242694 Dec 11 00:19 stream_20251211T001623_000001.gz.ready
-rw-r--r-- 1 dataacq dataacq  151407 Dec 11 00:20 stream_20251211T002001_000001.gz
cl@wikiacq:~$
```
**The program is writing files again. -> OK**

### Remark on HTTP Status Port
For remote checking of the status of the program, a HTTP server is available.
In the configuration described in this document, the server is active on port 9090. Before activating it, you should understand the risks that come with opening sockets and operating servers and take necessary the precautions, such as firewalling.

If the program has been receiving at least one event from Wikimedia, we will get a [HTTP status 200](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes):
```
cl@clpc:/tmp$ curl --head http://192.168.122.100:9090/check
HTTP/1.1 200 OK
date: Thu, 11 Dec 2025 00:21:30 GMT
content-length: 0

cl@clpc:/tmp$
```
GET requests are also supported.

On the other hand, if no event has been received in the previous 900 seconds (time can be adjusted at the top of file `wikistreamreader.py`), then this HTTP request returns HTTP status 500 (Internal Server Error). A website monitoring tool will consider this status as "down" and trigger an alert.
