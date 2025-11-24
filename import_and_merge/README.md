# README
## List of Resources
This directory contains the following resources:
* Version 1 (now historic) of the import-and-merge scripts
* [The DAGs for Apache Airflow version 3.1.3](airflow_dags/). They were developed with the Airflow developer version based on a single `docker-compose.yaml` file. Here, these are to be placed into the `dags/` directory. At least this configuration does not support the import from the modules when they are in a subdirectory of `dags/`.

## current implementation
In combination with the transfer script running as traditional cronjob,
a few Airflow DAGs are used to load the data in the data table.

![graph](../doc/img/jobgraph.png)

Once the most recent files with stream dumps have been downloading to the local data directory, the Airflow DAGs are triggered via a REST API request (internally this is a HTTP POST request). This API request also crosses between different Linux users, since the cronjob for data downloads runs with a different user id (that also is the owner of the data files).

