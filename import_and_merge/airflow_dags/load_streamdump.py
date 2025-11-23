import datetime
import pendulum
import os
from pathlib import Path

import requests
from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from filedb_util import fileDB_updatetimestamp,fileDB_updateeventstats
from load_streamdump_cfg import get_cfg

####################
### BEGIN CONFIG ###

cfg = get_cfg()
DATADIR = cfg['DATADIR']
DB_CONN_ID = cfg['DB_CONN_ID']
IS_INERT = False # True

###  END CONFIG  ###
####################


@dag(
    dag_id="load_streamdump",
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1, # run only one of these at a time
    dagrun_timeout=datetime.timedelta(minutes=60),
)
def LoadStreamdump(list_of_files: list[str] = None):
    # this in turn does imports that might take some time -> avoid top level imports
    from wikiloader import WikiLoader

    @task
    def op_dummy():
        print('dummyop')

    def process_single_file(conn,cur,filename_rel: str):
        print(f'* process_single_file for {filename_rel} *')
        if IS_INERT:
            return # for debugging

        # check DB connection
        query = 'SELECT 1;'
        cur.execute(query)

        print(filename_rel)
        filename = str(DATADIR / filename_rel)
        print(filename)
        fileDB_updatetimestamp(conn,cur,filename_rel,timestamptype='load_begin')
        wl = WikiLoader()
        rowcount_file = wl.data_load(cur,filename,True)
        rowcount_initial = wl.data_addhashes(cur) # no deduplication here, so it should correspond to number of loaded rows
        rowcount_hash_dedupl = wl.data_dedupl(cur)
        rowcount_final_merge = wl.data_merge(cur)
        fileDB_updatetimestamp( conn,cur,filename_rel, timestamptype='load_complete')
        fileDB_updateeventstats(conn,cur,filename_rel, rowcount_file,rowcount_final_merge)
        print(f'{rowcount_file} -> {rowcount_initial} -> {rowcount_hash_dedupl} -> {rowcount_final_merge}')
        return

    @task
    def op_importdatafiles(list_of_files: list[str] = None):
        print(f'*** op_importdatafiles: preparing import for {list_of_files} ***')
        # if user provided a single string instead of a list[str] -> be user-friendly and convert it into list of a single string
        if isinstance(list_of_files, str):
            print('Info: converting argument of type str to list[str]')
            list_of_files = [list_of_files]

        if isinstance(list_of_files, list) and all(isinstance(x,str) for x in list_of_files):
            print('type check OK')
            postgres_hook = PostgresHook(postgres_conn_id=DB_CONN_ID)
            conn = postgres_hook.get_conn()
            print(conn)
            cur = conn.cursor()
            for f_ in list_of_files:
                process_single_file(conn,cur,f_)
            # commit only ONCE, after all trying to load all files in set
            conn.commit()
            return

        print('*** op_importdatafiles: unexpected data type -> doing nothing ***')
        # FIXME: raise better fitting exception here
        raise ValueError(f'in op_importdatafiles: invalid/unexpected type of argument passed {str(type(list_of_files))}')

    # triggers DAG that updates MATERIALIZED VIEWs etc.
    trigger = TriggerDagRunOperator(
        task_id="trigger_load_streamdump_finalize",
        trigger_dag_id="load_streamdump_finalize",
    )

    op_dummy() >> op_importdatafiles(list_of_files) >> trigger


dag = LoadStreamdump()
