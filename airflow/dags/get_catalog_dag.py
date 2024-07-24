from airflow import DAG

from airflow.operators.python import PythonOperator

from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from airflow.models import TaskInstance
from datetime import datetime
import os
import sqlparse
import pandas as pd
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine

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


def get_datasets_catalog(select: list[str], ti: TaskInstance):
    """
    Get the catalog data from the Paris 2024 API

    Args:
        select (list): list of columns to select
        ti (TaskInstance): TaskInstance object
    """
    data = pd.read_csv(
        "https://data.paris2024.org/api/explore/v2.1/catalog/exports/csv?delimiter=%3B&lang=fr",
        sep=";",
    )
    data.columns = [col.replace("default.", "") for col in data.columns]
    filtered_data = data[select].copy()
    filtered_data["tablename"] = filtered_data["datasetid"].str.replace("-", "_")
    ti.xcom_push(key="jo_datasets", value=filtered_data)


def add_jo_dataset_to_postgres(db_params: dict, ti: TaskInstance):
    """
    Add the catalog data to the PostgreSQL database

    Args:
        db_params (dict): dictionary of database connection parameters
        ti (TaskInstance): TaskInstance object
    """
    # Retrieve the jo_datasets from XCom
    jo_datasets: pd.DataFrame = ti.xcom_pull(
        key="jo_datasets", task_ids="get_jo_datasets_catalog"
    )
    # Create a connection to the PostgreSQL database
    engine = create_engine(
        f"postgresql://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    )
    jo_datasets.to_sql("datasets", engine, if_exists="replace", index=False)


sql = get_sql_queries("queries.sql")

create_table_statement = sqlparse.split(sql)


with DAG(
    "fetch_jo_datasets",
    start_date=datetime(2024, 7, 16),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    create_table = SQLExecuteQueryOperator(
        task_id="create_pg_table",
        sql=create_table_statement,
        conn_id="storage_conn",
        autocommit=True,
    )

    get_dataset = PythonOperator(
        task_id="get_jo_datasets_catalog",
        python_callable=get_datasets_catalog,
        op_args=[COLUMNS],
    )

    add_jo_dataset = PythonOperator(
        task_id="add_jo_datasets_to_postgres",
        python_callable=add_jo_dataset_to_postgres,
        op_args=[conn_config],
    )

    create_table >> get_dataset >> add_jo_dataset
