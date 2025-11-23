from pathlib import Path

def get_cfg():
    cfg = {
        # data directory seen from INSIDE of the Docker container
        # 'DATADIR': Path('/opt/airflow/dags/'),
        'DATADIR': Path('/mnt/'),
        'DB_CONN_ID': 'dev_wikidb',
    }
    return cfg
