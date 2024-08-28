from airflow import DAG

from airflow.operators.python import PythonOperator

from airflow.models import TaskInstance
from datetime import datetime
import os
import pandas as pd
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
import psycopg2

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)

pg_conn = BaseHook.get_connection("storage_conn")
hostname = pg_conn.host
username = pg_conn.login
password = pg_conn.password
database = pg_conn.schema
port = pg_conn.port
conn_config = {
    "host": hostname,
    "username": username,
    "password": password,
    "database": database,
    "port": port,
}

def get_data_file(path: str):
    dir = os.path.dirname(__file__)
    query_file = os.path.join(dir, path)
    return query_file
def get_sql_queries(query_file) -> str:
    """
    Get the SQL queries from a file

    Args:
        query_file (str): file containing the SQL queries

    Returns:
        str: SQL queries
    """
    # get the dir of the current file
    dir = os.path.dirname(__file__)
    query_file = os.path.join(dir, query_file)
    with open(query_file) as file:
        return file.read()


COLUMNS = [
    "title",
    "description",
    "theme",
    "keyword",
    "modified",
    "publisher",
    "records_count",
    "datasetid",
]


def get_datasets_catalog(path: str, output_key: str, ti: TaskInstance):
    """
    Get the catalog data from the Paris 2024 API

    Args:
        select (list): list of columns to select
        ti (TaskInstance): TaskInstance object
    """
    data_path = get_data_file(path=path)
    data = pd.read_json(
        data_path
    )
    print("Data fetched from API")
    print(data)
    ti.xcom_push(key=output_key, value=data)


def add_jo_dataset_to_postgres(db_params: dict, table: str,input_key: str,  ti: TaskInstance):
    """
    Add the catalog data to the PostgreSQL database

    Args:
        db_params (dict): dictionary of database connection parameters
        ti (TaskInstance): TaskInstance object
    """
    # Retrieve the jo_datasets from XCom
    print("Adding data to postgres")
    print(ti.previous_ti)

    jo_datasets: pd.DataFrame = ti.xcom_pull(
        key=input_key, task_ids=input_key
    )
    # Create a connection to the PostgreSQL database
    engine = create_engine(
        f"postgresql://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    )
    jo_datasets.to_sql(table, engine, if_exists="replace", index=False)


# sql = get_sql_queries("queries.sql")

# create_table_statement = sqlparse.split(sql)

# schedule to run all the 10 minutes
with DAG(
    "fetch_jo_medals",
    start_date=datetime(2024, 7, 16),
    schedule_interval="*/5 * * * *",
    catchup=False,
) as dag:


    get_dataset = PythonOperator(
        task_id="get_jo_medals",
        python_callable=get_datasets_catalog,
        op_args=["data/countries_medals.json", "get_jo_medals"],
    )


    add_countries_medals_dataset = PythonOperator(
        task_id="add_jo_medals_to_postgres",
        python_callable=add_jo_dataset_to_postgres,
        op_args=[conn_config, "countries_medals", "get_jo_medals"],
    )



    get_athletes_dataset = PythonOperator(
        task_id="get_jo_athletes_medals",
        python_callable=get_datasets_catalog,
        op_args=["data/athletes_medals.json", "get_jo_athletes_medals"],
    )
    add_athletes_medals_dataset = PythonOperator(
        task_id="add_jo_athletes_medals_to_postgres",
        python_callable=add_jo_dataset_to_postgres,
        op_args=[conn_config, "athletes_medals", "get_jo_athletes_medals"],
    )
    get_dataset >> add_countries_medals_dataset 
    get_athletes_dataset >> add_athletes_medals_dataset
