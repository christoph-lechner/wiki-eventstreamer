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
