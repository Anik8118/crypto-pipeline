import os

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

PROJECT = os.environ["GCP_PROJECT_ID"]
DATASET = "crypto_raw"
TABLE = "crypto_prices"


def read_postgres():
    engine = create_engine(
        URL.create(
            "postgresql+psycopg2",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.environ["POSTGRES_DB"],
        )
    )
    df = pd.read_sql(
        "SELECT coin, price_usd, price_time, fetched_at "
        "FROM crypto_prices ORDER BY price_time",
        engine,
    )
    df["price_usd"] = df["price_usd"].astype(float)
    return df


def load_bigquery(df):
    client = bigquery.Client(project=PROJECT)
    table_id = f"{PROJECT}.{DATASET}.{TABLE}"
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("coin", "STRING"),
            bigquery.SchemaField("price_usd", "FLOAT"),
            bigquery.SchemaField("price_time", "TIMESTAMP"),
            bigquery.SchemaField("fetched_at", "TIMESTAMP"),
        ],
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}")


if __name__ == "__main__":
    df = read_postgres()
    print(f"Read {len(df)} rows from PostgreSQL")
    load_bigquery(df)