CL, 2026-01-03

The used version of `remove_old_streamdumps.py` is from git commit id 8f13034 (Dec 15, 2025, 19:58).

Place the script into a directory of choice. The script has to run as user `dataacq`, this is the owner of the files containing the stream dumps. Since the script does not require any special Python packages, no virtual environment is needed.

These are the permissions on the data acquisition system of my demo installation:
```
dataacq@wikiacq:~/wiki/prod-remove_old_streamdumps$ ls -l
total 4
-rwxr-xr-x 1 dataacq dataacq 3554 Jan  2 23:35 remove_old_streamdumps.py
```

If you run the script **without** `--delete` argument, it is in a "dry-run mode". Then files considered too old are only listed but not removed:
```
dataacq@wikiacq:~/wiki/prod-remove_old_streamdumps$ ./remove_old_streamdumps.py --dir=/srv/wikiproj/streamdata_in/ --max-age-in-days=21
reporting: too old file /srv/wikiproj/streamdata_in/stream_20251211T001623_000001.gz.ready
reporting: too old file /srv/wikiproj/streamdata_in/stream_20251211T002001_000001.gz.ready
[..]
reporting: too old file /srv/wikiproj/streamdata_in/stream_20251212T230500_000048.gz.ready
```

Once you are satisifed with the configuration, let's proceed.
First of all, it is always a good idea to write a tar archive of your data directory so you can roll back in case you don't like the result. 
Then, while logged in as `dataacq` user, run `crontab -e` command to add it to the crontab of user `dataacq` to schedule execution every day at midnight:
```
0 0 * * * /usr/bin/flock -n /tmp/wiki-remove_old_streamdumps-cron.lockfile /home/dataacq/wiki/prod-remove_old_streamdumps/remove_old_streamdumps.py --dir=/srv/wikiproj/streamdata_in/ --max-age-in-days=21 --delete
```
