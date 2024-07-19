from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from datetime import timedelta
import requests
import json
import psycopg2

BASE_URL = "https://data.paris2024.org/api/explore/v2.1/catalog/datasets/"

pg_conn = BaseHook.get_connection("storage_conn")

hostname = pg_conn.host
username = pg_conn.login
password = pg_conn.password
database = pg_conn.schema

conn_config = {
    "host": hostname,
    "username": username,
    "password": password,
    "database": database,
    "port": 5432,
}


def get_data_from_postgres(db_params: dict):
    engine = create_engine(
        f"postgresql://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    )
    data = pd.read_sql("SELECT datasetid, records_count FROM datasets", engine)
    datasets = data.to_dict("records")
    print("Data fetched from Postgres")
    return datasets


psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


def create_dataset_dag(dag_id, dataset_id, records_count, db_params):
    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(2024, 7, 16),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    with DAG(
        dag_id, default_args=default_args, schedule_interval="@daily", catchup=False
    ) as dag:

        def fetch_batch(**kwargs):
            batch_number = kwargs["batch_number"]
            offset = batch_number * 100
            url = f"{BASE_URL}/{dataset_id}/records?limit=100&offset={offset}"
            response = requests.get(url)
            data = response.json()["results"]
            df = pd.DataFrame(data)
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, dict)).all():
                    df[col] = df[col].apply(lambda x: json.dumps(x))
            engine = create_engine(
                f"postgresql://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
            )
            tablename = dataset_id.replace("-", "_")
            df.to_sql(tablename, engine, if_exists="append", index=False)

        num_batches = (records_count + 99) // 100  # Round up to nearest hundred
        for i in range(num_batches):
            PythonOperator(
                task_id=f"fetch_batch_{i}",
                python_callable=fetch_batch,
                op_kwargs={"batch_number": i},
                dag=dag,
            )

    return dag


# Generate DAGs dynamically
datasets_info = get_data_from_postgres(conn_config)
for dataset in datasets_info:
    dag_id = f"process_{dataset['datasetid']}"
    create_dataset_dag(
        dag_id, dataset["datasetid"], dataset["records_count"], conn_config
    )

