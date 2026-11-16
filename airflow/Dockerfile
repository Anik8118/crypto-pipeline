FROM apache/airflow:3.2.0

RUN pip install --no-cache-dir requests pandas sqlalchemy

RUN python -m venv /home/airflow/dbt_venv \
    && /home/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-core dbt-postgres