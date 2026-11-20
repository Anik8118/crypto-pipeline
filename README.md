# Crypto Price ETL Pipeline

An end-to-end data engineering project: it collects cryptocurrency prices from a public API every hour, stores them in PostgreSQL, transforms them with dbt, tests the results, and orchestrates everything with Apache Airflow.

## Architecture

CoinGecko API -> pipeline.py (Python, pandas) -> PostgreSQL (raw table) -> dbt (staging view + daily summary table) -> dbt tests

The whole flow is scheduled hourly by an Airflow DAG running in Docker.

## What each part does

- **Extract / Load (pipeline.py):** fetches Bitcoin, Ethereum and Solana prices (USD), converts timestamps to UTC, and inserts them into `public.crypto_prices`. It is idempotent: the primary key `(coin, price_time)` with `ON CONFLICT DO NOTHING` prevents duplicates.
- **Transform (crypto_dbt/):** a dbt project with a staging model (`stg_crypto_prices`, a view) and a mart model (`daily_price_summary`, a table) in the `analytics` schema.
- **Data quality:** dbt tests check for nulls and accepted coin names.
- **Orchestration (airflow/):** the `crypto_pipeline` DAG runs `run_pipeline -> dbt_run -> dbt_test` every hour.

## Project structure

```
pipeline.py            ETL script
docker-compose.yml     PostgreSQL
crypto_dbt/            dbt project (models, tests)
airflow/               Airflow in Docker (Dockerfile, compose files, DAGs)
```

## Configuration

Secrets are not stored in the repository. Create a `.env` file in the project root from the example:

```
copy .env.example .env
```

Then set `POSTGRES_PASSWORD` to your own value. For Airflow, create `airflow/.env` with `AIRFLOW_UID`, `AIRFLOW_IMAGE_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`.


## How to run

1. Start PostgreSQL:

```
docker compose up -d
```

2. Run the ETL script once by hand:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python pipeline.py
```

3. Run dbt by hand (dbt Core with the Postgres adapter, Python 3.12 or 3.13):

```
cd crypto_dbt
dbt run
dbt test
```

4. Run everything with Airflow:

```
cd airflow
echo AIRFLOW_UID=50000> .env
echo AIRFLOW_IMAGE_NAME=crypto-airflow:1.0>> .env
docker build -t crypto-airflow:1.0 .
docker compose up airflow-init
docker compose up -d
```

Open http://localhost:8080 (user and password: airflow), switch on the `crypto_pipeline` DAG and trigger it.

## Tech stack

Python, pandas, SQLAlchemy, PostgreSQL, dbt, Apache Airflow, Docker

## Roadmap

- Dashboard for the price history
- Move secrets out of the repository
- Cloud data warehouse (for example BigQuery)

## Configuration

Secrets are not stored in the repository. Create a `.env` file in the project root from the example:

```
copy .env.example .env
```

Then set `POSTGRES_PASSWORD` to your own value. For Airflow, create `airflow/.env` with `AIRFLOW_UID`, `AIRFLOW_IMAGE_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`.



## BigQuery

The same dbt models also run on Google BigQuery (sandbox, no billing needed).

1. Create a Google Cloud project and a dataset called `crypto_raw`.
2. Log in with `gcloud auth application-default login` and set `GCP_PROJECT_ID` in `.env`.
3. Load the raw table: `python load_to_bigquery.py`
4. Add a `bq` target (BigQuery, oauth) to your dbt profile, then:

```
dbt run --target bq
dbt test --target bq
```

The dashboard has a sidebar switch to read from BigQuery or PostgreSQL.