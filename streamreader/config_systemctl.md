# Setup of systemctl Service
Prerequisite: User name for running the service was already created. The user name is specified in the `.service` file with parameter `User` in the `[Service]` section.

## Preparations of Python Environment
```
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ python3 -m venv /home/dataacq/venv_wikistreamreader_prod/
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ source /home/dataacq/venv_wikistreamreader_prod/bin/activate
(venv_wikistreamreader_prod) dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ pip install -r requirements.txt 
[..]
Successfully installed certifi-2025.10.5 charset_normalizer-3.4.4 idna-3.11 requests-2.32.5 requests-sse-0.5.2 urllib3-2.5.0
```

## Setup of the service
OS: Ubuntu Server 22.04 LTS

Copy the file `wikistreamreader.service` to `/etc/systemd/system/`,
then enable the service
```
cl@ubuntu:~$ sudo systemctl enable wikistreamreader
Created symlink /etc/systemd/system/multi-user.target.wants/wikistreamreader.service → /etc/systemd/system/wikistreamreader.service.
cl@ubuntu:~$
```

## Running the service
Now, let's start the service:
```
cl@ubuntu:~$ sudo systemctl start wikistreamreader
```

Let's check the status:
```
cl@ubuntu:~$ sudo systemctl status wikistreamreader
● wikistreamreader.service - CL's wiki stream reader
     Loaded: loaded (/etc/systemd/system/wikistreamreader.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-11-10 23:20:34 UTC; 15s ago
   Main PID: 2630047 (run_wikistreamr)
      Tasks: 2 (limit: 2188)
     Memory: 25.2M
        CPU: 7.571s
     CGroup: /system.slice/wikistreamreader.service
             ├─2630047 /bin/bash /home/dataacq/wiki/wiki-eventstreamer/streamreader/run_wikistreamreader.sh
             └─2630049 python3 ./wikistreamreader.py

Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ _OLD_VIRTUAL_PS1=
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ PS1='(venv_wikistreamreader_prod) '
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ export PS1
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ VIRTUAL_ENV_PROMPT='(venv_wikistreamreader_prod) '
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ export VIRTUAL_ENV_PROMPT
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ '[' -n /bin/bash -o -n '' ']'
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: ++ hash -r
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630047]: + ./wikistreamreader.py
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630049]: Opened output file /srv/wikiproj/streamdata_in/stream_20251110T232034_000001.gz
Nov 10 23:20:34 ubuntu run_wikistreamreader.sh[2630049]: No checkpoint was found!
cl@ubuntu:~$
```

Finally, we can read the logs later using:
```
cl@ubuntu:~$ sudo journalctl -u wikistreamreader
```
