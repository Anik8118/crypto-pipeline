from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"
DBT = "/home/airflow/dbt_venv/bin/dbt"
PROFILES = f"{PROJECT}/airflow/dbt_profiles"

with DAG(
    dag_id="crypto_pipeline",
    start_date=datetime(2026, 11, 1),
    schedule="@hourly",
    catchup=False,
) as dag:
    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command=f"python {PROJECT}/pipeline.py",
        env={"DB_URL": "postgresql+psycopg2://de_user:de_pass@host.docker.internal:5432/crypto"},
        append_env=True,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT}/crypto_dbt && {DBT} run --profiles-dir {PROFILES}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT}/crypto_dbt && {DBT} test --profiles-dir {PROFILES}",
    )

    run_pipeline >> dbt_run >> dbt_test