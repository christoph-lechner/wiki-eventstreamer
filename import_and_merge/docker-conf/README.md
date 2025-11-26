# README
Note that, as pointed out in [the Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html), **this setup is not suitable for production use.**

## Changes to docker-compose.yaml
This directory contains the `docker-compose.yaml` file that can be used to get Airflow running in Docker.
It is based on the file from the Airflow documentation, with a few changes to adopt it to my specific setup. In particular, this includes changes to mount the directory with the production data files (`/srv/wikidata/in`) to `/mnt` inside of the containers. The additional GID of 1001 is required to have read-only access to data files.

## Further preparations
For the general preparation procedure, follow the steps described [here](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

The DAGs developed for this project can be found in this repository.

## Preparations for Triggering via REST API
To trigger the DAG runs via the REST API, a username has to be created in Airflow. With the containers up and running, I executed the following command (in the directory where the `docker-compose.yaml` file is situated) to create the account `cltest` (here done with Admin priviledges, this should be adjusted accordingly):
```
docker compose exec airflow-scheduler airflow users create --username cltest --firstname C --lastname L --role Admin -e "cl@cl"
```

### Testing It
Following https://airflow.apache.org/docs/apache-airflow/stable/security/api.html

Request:
```
curl -X POST http://localhost:9080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cltest",
    "password": "[...]"
  }'
```
If everything is working, the response has the structure:
```
{"access_token":"[...]"}
```
We have obtained the JWT token to be included in requests.

After configuration of the `wiki-eventstreamer-transfer` software, the program `./obtain_JWT.py` should be used to check that the JWT token can be obtained.
