from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

INGESTION_DIR = "/opt/airflow/workspace/ingestion/src"
DBT_DIR = "/opt/airflow/workspace/seattle_erp"

with DAG(
    dag_id="emergency_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    ingest_data = BashOperator(
        task_id="ingest_data",
        bash_command=f"""
        python {INGESTION_DIR}/main.py
        """
    )

    run_dbt_silver = BashOperator(
        task_id="run_dbt_silver",
        bash_command=f"""
        cd {DBT_DIR} &&
        dbt run --select silver
        """
    )

    run_dbt_gold = BashOperator(
        task_id="run_dbt_gold",
        bash_command=f"""
        cd {DBT_DIR} &&
        dbt run --select gold
        """
    )

    run_tests = BashOperator(
        task_id="run_tests",
        bash_command=f"""
        cd {DBT_DIR} &&
        dbt test
        """
    )

    ingest_data >> run_dbt_silver >> run_dbt_gold >> run_tests
