# README
## List of Resources
This directory contains the following resources:
* Version 1 (now historic) of the import-and-merge scripts
* [The DAGs for Apache Airflow version 3.1.3](airflow_dags/). They were developed with the Airflow developer version based on a single `docker-compose.yaml` file. Here, these are to be placed into the `dags/` directory. At least this configuration does not support the import from the modules when they are in a subdirectory of `dags/`.

## Implementation with Airflow
In combination with the transfer script running as traditional cronjob,
a few Airflow DAGs are used to load the data in the data table.

![graph](../doc/img/jobgraph.png)

Once the most recent files with stream dumps have been downloading to the local data directory, the Airflow DAGs are triggered via a REST API request (internally this is a HTTP POST request). This API request also "crosses" between different Linux users, since the cronjob for data downloads runs with a different user id (this user is also owner of the data files).

### Configuration Detail
The cronjob for data transfer is currently configured to run at minute 10 of every hour as follows:
```
wikidata@clsrv:~$ crontab -l
[..]

10 * * * * /usr/bin/flock -n /tmp/wiki-transfer-cron.lockfile /home/wikidata/prod_transfer/wiki-eventstreamer-transfer/run_cron.sh
```
The `flock` command ([manpage](https://man7.org/linux/man-pages/man1/flock.1.html)) ensures that at most one instance of the transfer program is running. As the transfer process has a normal runtime of about 1 minute, this is only a protection in the case of malfunction.
