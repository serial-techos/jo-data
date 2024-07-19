# JO-data

### Project Overview

This project focuses on the ingestion and exploitation of data from the Olympic Games. Using a combination of Python, SQL, Airflow, and PostgreSQL, we aim to create an efficient pipeline for extracting, transforming, and loading (ETL) data from various sources into a structured database. The goal is to facilitate data analysis and the creation of various data-driven applications.

### Repository Structure

```
jo-data/
├── airflow/
│   ├── dags/
│   │   ├── __init__.py
│   │   ├── get_catalog_dag.py
│   │   └── ingest_datasets_dag.py
│   ├── docker-compose.yaml
│   ├── .dockerignore
│   ├── .gitignore
│   ├── requirements.txt
│   └── settings.py
```

### Files and Directories

- **airflow/**: This directory contains all configurations and scripts related to Apache Airflow.
  - **dags/**: Contains the Directed Acyclic Graphs (DAGs) that define the workflows for data ingestion and transformation.
    - **get_catalog_dag.py**: DAG for retrieving data catalog from the API.
    - **ingest_datasets_dag.py**: DAG for ingesting datasets from the API into the PostgreSQL database.
  - **docker-compose.yaml**: Configuration file to set up the Airflow environment using Docker.

### Getting Started

#### Prerequisites

- Docker
- Docker Compose

#### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/jo-data.git
   cd jo-data/airflow
   ```

2. **Build and start the Docker containers:**
   ```sh
   docker-compose up -d
   ```

3. **Access the Airflow web interface:**
   Open your browser and go to `http://localhost:8080`.

#### Airflow Configuration

- The Airflow web server will be available at `http://localhost:8080`.
- Use the default credentials to log in: 
  - Username: `airflow`
  - Password: `airflow`

### Usage

1. **Set up the Airflow environment:**
   - Ensure Docker and Docker Compose are installed on your machine.
   - Navigate to the `airflow` directory.
   - Run `docker-compose up -d` to start the Airflow services.

2. **Trigger the DAGs:**
   - Go to the Airflow web interface.
   - Enable and trigger the DAGs (`get_catalog_dag` and `ingest_datasets_dag`) as needed.

3. **Monitor the DAGs:**
   - Check the status and logs of the DAG runs in the Airflow web interface to ensure the tasks are executed successfully.

### Contributing

We welcome contributions to enhance the project. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch to your fork.
4. Open a pull request with a detailed description of your changes.


