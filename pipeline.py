import os

import pandas as pd
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_db_url():
    # Airflow এখনো পুরো DB_URL পাঠায়, থাকলে সেটাই ব্যবহার হবে
    full_url = os.getenv("DB_URL")
    if full_url:
        return full_url
    return URL.create(
        "postgresql+psycopg2",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )


def extract():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,solana",
        "vs_currencies": "usd",
        "include_last_updated_at": "true",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def transform(data):
    rows = []
    for coin, values in data.items():
        rows.append({
            "coin": coin,
            "price_usd": values["usd"],
            "price_time": values["last_updated_at"],
        })
    df = pd.DataFrame(rows)
    # Unix সেকেন্ডকে সাধারণ তারিখ-সময়ে বদলানো
    df["price_time"] = pd.to_datetime(df["price_time"], unit="s", utc=True)
    df["fetched_at"] = pd.Timestamp.now(tz="UTC")
    return df


def load(df, engine):
    create_sql = """
    CREATE TABLE IF NOT EXISTS crypto_prices (
        coin TEXT NOT NULL,
        price_usd NUMERIC NOT NULL,
        price_time TIMESTAMPTZ NOT NULL,
        fetched_at TIMESTAMPTZ NOT NULL,
        PRIMARY KEY (coin, price_time)
    )
    """
    insert_sql = """
    INSERT INTO crypto_prices (coin, price_usd, price_time, fetched_at)
    VALUES (:coin, :price_usd, :price_time, :fetched_at)
    ON CONFLICT (coin, price_time) DO NOTHING
    """
    with engine.begin() as conn:
        conn.execute(text(create_sql))
        conn.execute(text(insert_sql), df.to_dict("records"))


if __name__ == "__main__":
    engine = create_engine(get_db_url())
    raw = extract()
    df = transform(raw)
    print(df)
    load(df, engine)
    print("Done: data loaded into PostgreSQL")