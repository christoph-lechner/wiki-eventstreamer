# README
Note that, as pointed out in [the Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html), **this setup is not suitable for production use.**

## Changes to docker-compose.yaml
This directory contains the `docker-compose.yaml` file that can be used to get Airflow running in Docker.
It is based on the file from the Airflow documentation, with a few changes to adopt it to my specific setup. In particular, this includes changes to mount the directory with the production data files (`/srv/wikidata/in`) to `/mnt` inside of the containers. The additional GID of 1001 is required to have read-only access to data files.

## Further preparations
For the general preparation procedure, follow the steps described [here](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

The DAGs developed for this project can be found in this repository.

To trigger the DAG runs via the REST API, a username has to be created in Airflow. -> document this.
