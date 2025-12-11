* 6GB RAM, 2 CPUs
* 100GB of disk (70GB for `/`, 2GB for `/boot`)
* installation with default configuration "Ubuntu Server"
* install openssh server
* hostname wikisrv

## Installation of Docker
Following the official installation instructions
https://docs.docker.com/engine/install/ubuntu/

Remove conflicting packages:
```
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc | cut -f1)
```

Before we begin, let's upgrade all installed packages:
```
sudo apt-get update
sudo apt-get upgrade
```

From the docker installation instructions
```
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

```
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```
cl@wikisrv:~$ sudo docker run hello-world
```

Optional:
add user to group docker to run without sudo



```
cl@wikisrv:~$ mkdir work
cl@wikisrv:~$ cd work
cl@wikisrv:~/work$ git clone https://github.com/christoph-lechner/wiki-eventstreamer.git
Cloning into 'wiki-eventstreamer'...
remote: Enumerating objects: 947, done.
remote: Counting objects: 100% (98/98), done.
remote: Compressing objects: 100% (71/71), done.
remote: Total 947 (delta 40), reused 74 (delta 27), pack-reused 849 (from 1)
Receiving objects: 100% (947/947), 1.95 MiB | 6.16 MiB/s, done.
Resolving deltas: 100% (533/533), done.
cl@wikisrv:~/work$
```



## Preparation of PostgreSQL DB
```
cl@wikisrv:~$ sudo useradd -m -c "user for wiki data storage" -s /bin/bash wikidata
cl@wikisrv:~$ sudo useradd -m -c "user for wiki proj" -s /bin/bash wikiproj
cl@wikisrv:~$ sudo useradd -m -c "user for wiki proj DB" -s /bin/bash wikipg
```

```
cl@wikisrv:~$ sudo mkdir /srv/postgres-data-wiki
cl@wikisrv:~$ sudo chown wikipg:wikipg /srv/postgres-data-wiki/
```

**Modification of docker-compose.yaml file for the DB to run with this user**
```
cl@wikisrv:~/work/wiki-eventstreamer/db$ id wikipg
uid=1003(wikipg) gid=1003(wikipg) groups=1003(wikipg)
cl@wikisrv:~/work/wiki-eventstreamer/db$
```

**DB config: git commit ID ac71132**

The default passwords for postgres and pgadmin need to be changed. Note that the default password for postgres in docker-compose.yaml is only effective for the first time when the DB is initialized.



```
postgres@127.0.0.1:postgres> CREATE USER wikiproj WITH PASSWORD 'your_password';
CREATE ROLE
Time: 0.023s
postgres@127.0.0.1:postgres> CREATE DATABASE wikidb OWNER wikidb;
role "wikidb" does not exist
Time: 0.026s
postgres@127.0.0.1:postgres> CREATE DATABASE wikidb OWNER wikiproj;
CREATE DATABASE
Time: 0.114s
postgres@127.0.0.1:postgres>
```
Verify that we can connect as `wikiproj` to the `wikidb` and that we can create a simple table there (and insert a row).

```
postgres@127.0.0.1:postgres> CREATE USER wikiproj_ro WITH PASSWORD 'your_ro_password';
CREATE ROLE
Time: 0.023s
postgres@127.0.0.1:postgres> GRANT CONNECT ON DATABASE wikidb TO wikiproj_ro;
GRANT
Time: 0.016s
postgres@127.0.0.1:postgres> \c wikidb
You are now connected to database "wikidb" as user "postgres"
Time: 0.075s
postgres@127.0.0.1:wikidb> GRANT USAGE ON SCHEMA public TO wikiproj_ro;
GRANT
Time: 0.015s
postgres@127.0.0.1:wikidb> GRANT SELECT ON ALL TABLES IN SCHEMA public TO wikiproj_ro;
GRANT
Time: 0.016s
postgres@127.0.0.1:wikidb>
```
Above commands granted SELECT permission to `wikiproj_ro` on all tables that are already existing in database `wikidb`. What is still missing is adjusting the permissions for tables that will be created in the future.
As `wikiproj` will be creating all the tables in the database `wikidb`, the following command must be executed as user `wikiproj` (**not as superuser 'postgres'**):
```
wikiproj@127.0.0.1:wikidb> ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON 
 TABLES TO wikiproj_ro;
You're about to run a destructive command.
Do you want to proceed? [y/N]: y
Your call!
ALTER DEFAULT PRIVILEGES
Time: 0.020s
wikiproj@127.0.0.1:wikidb>
```


From `file_transfer.py`, commit id c13ae95
```
CREATE TABLE wiki_datafiles(
    filename TEXT UNIQUE,
    file_hash TEXT,
    filename_xferlog TEXT,
    ts_entry_creation TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ts_file_transfer TIMESTAMP WITH TIME ZONE,
    ts_load_begin TIMESTAMP WITH TIME ZONE,
    ts_load_end TIMESTAMP WITH TIME ZONE,
    loadstat_events_in_file INT,
    loadstat_events_merged INT,
    ts_file_archive TIMESTAMP WITH TIME ZONE
);
```

From `20251109_plotoptim.md`, commit id 4189a70, Partitionierung ziemlich weit unten.
```
CREATE TABLE wiki_change_events_test(
    -- MD5 hash over a few fields, ensures deduplication (data is loaded into this table using MERGE command)
    _h TEXT,
    ts_event_meta_dt TIMESTAMP WITH TIME ZONE,
    event_meta_dt TEXT,
    event_meta_id TEXT,
    event_meta_domain TEXT,
    event_id BIGINT,
    event_type TEXT,
    event_wiki TEXT,
    event_user TEXT,
    event_bot BOOLEAN,
    event_title TEXT,
    UNIQUE(_h,event_wiki)
) PARTITION BY LIST(event_wiki);
CREATE TABLE wiki_change_events_test_dewiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('dewiki');
CREATE TABLE wiki_change_events_test_enwiki
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('enwiki');
CREATE TABLE wiki_change_events_test_hightraffic
	PARTITION OF wiki_change_events_test
	FOR VALUES IN ('commonswiki','wikidatawiki');
CREATE TABLE wiki_change_events_test_otherwikis
	PARTITION OF wiki_change_events_test DEFAULT;
```

From `doc/schema.md`, commit id `16bbb6c`
```
CREATE MATERIALIZED VIEW wiki_matview_countsall AS
SELECT
        DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
        COALESCE( SUM(1),0 ) AS count_bot_flagignore,
        COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
        COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events
WHERE
        -- the streamreader rotates the stream dumps no at the full hour
        -- -> cut away the final (incomplete) hour
        ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events) 
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki;

CREATE MATERIALIZED VIEW wiki_matview_countsedits AS
SELECT
        DATE(ts_event_meta_dt) AS date, EXTRACT(HOUR FROM ts_event_meta_dt) AS hour,event_wiki,
        COALESCE( SUM(1),0 ) AS count_bot_flagignore,
        COALESCE( SUM((CASE WHEN event_bot=TRUE  THEN 1 END)),0 ) AS count_bot_true,
        COALESCE( SUM((CASE WHEN event_bot=FALSE THEN 1 END)),0 ) AS count_bot_false
FROM wiki_change_events
WHERE
        -- the streamreader rotates the stream dumps no at the full hour
        -- -> cut away the final (incomplete) hour
        ts_event_meta_dt<(SELECT DATE_TRUNC('HOUR',MAX(ts_event_meta_dt)) FROM wiki_change_events)
        AND event_type='edit'
GROUP BY date,hour,event_wiki
ORDER BY date,hour,event_wiki;
```
