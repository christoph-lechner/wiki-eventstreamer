```
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ python3 -m venv /home/dataacq/venv_wikistreamreader_prod/
dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ source /home/dataacq/venv_wikistreamreader_prod/bin/activate
(venv_wikistreamreader_prod) dataacq@demosrv:~/wiki/wiki-eventstreamer/streamreader$ pip install -r requirements.txt 
[..]
Successfully installed certifi-2025.10.5 charset_normalizer-3.4.4 idna-3.11 requests-2.32.5 requests-sse-0.5.2 urllib3-2.5.0
```

Copy the file `wikistreamreader.service` to `/etc/systemd/system/`,
then enable the service
```
cl@demosrv:~$ sudo systemctl enable wikistreamreader
```
