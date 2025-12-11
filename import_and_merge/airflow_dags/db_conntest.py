import datetime
import pendulum
import os
from pathlib import Path

import requests
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from load_streamdump_cfg import get_cfg
DB_CONN_ID = get_cfg()['DB_CONN_ID']

@dag(
    dag_id="db_conntest",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1, # run only one of these at a time
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def DB_conntest():
    @task
    def op_DBconntest():
        print('* start of DB conntest *')
        postgres_hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
        conn = postgres_hook.get_conn()
        cur = conn.cursor()

        # check DB connection
        query = 'SELECT 1;'
        cur.execute(query)

        print('* end of DB conntest *')

    op_DBconntest()


dag = DB_conntest()
