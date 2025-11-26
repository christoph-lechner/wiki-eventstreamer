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
    dag_id="load_streamdump_finalize",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1, # run only one of these at a time
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def LoadStreamdump_F():
    @task
    def op_updateMVs():
        def update_matview(cur,viewname):
            """
            Function that does the actual work. Added this to be able to use
            wrapper with parameter depending on argument to the outer function.
            """
            print(f'Updating view {viewname} ...')
            cur.execute(f'REFRESH MATERIALIZED VIEW {viewname};')

        matviews_to_update = ['wiki_matview_countsall', 'wiki_matview_countsedits']
        postgres_hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
        conn = postgres_hook.get_conn()
        cur = conn.cursor()
        for vn in matviews_to_update:
            update_matview(cur,vn)
        conn.commit()

    op_updateMVs()


dag = LoadStreamdump_F()
