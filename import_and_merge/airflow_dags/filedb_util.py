# based on orch_util.py, commit id b21b520 (Nov 11, 2025)
# import psycopg
import datetime

def fileDB_updatetimestamp(conn,cur,fn,timestamptype=None):
    # translate type into column in DB table
    ts_types = {
        'load_begin':      'ts_load_begin',
        'load_complete':   'ts_load_end',
        'archived':        'ts_file_archive',
    }
    if not timestamptype or timestamptype not in ts_types:
        raise ValueError('You have to specify type of timestamp')

    # Apache airflow 3.1.3 still uses psycopg2, so conn.transaction() is not available...
    """
    # ! NOTE according to https://www.psycopg.org/psycopg3/docs/basic/transactions.html#transaction-contexts ,
    # ! without autocommit, "with conn.transaction():" block does only sub-transaction.
    # ! A commit is still required!
    with conn.transaction():
        try:
            # using locally generated timestamp value instead of just SQL NOW() for consistency
            tnow = datetime.datetime.now()
            cur.execute(
                'UPDATE wiki_datafiles SET '+ts_types[timestamptype]+'=%s WHERE filename=%s;',
                (tnow,fn)
            )
        except psycopg.errors.UniqueViolation:
            pass
    """

    # using locally generated timestamp value instead of just SQL NOW() for consistency
    tnow = datetime.datetime.now()
    cur.execute(
        'UPDATE wiki_datafiles SET '+ts_types[timestamptype]+'=%s WHERE filename=%s;',
        (tnow,fn)
    )

def fileDB_updateeventstats(conn,cur,fn,N_in_file,N_merged):
    cur.execute(
        'UPDATE wiki_datafiles SET loadstat_events_in_file=%s, loadstat_events_merged=%s WHERE filename=%s;',
        (N_in_file,N_merged,fn)
    )
