import os

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROJECT = os.environ["GCP_PROJECT_ID"]

st.title("Crypto Price Dashboard")
source = st.sidebar.radio("Data source", ["BigQuery", "PostgreSQL"])


def table(name):
    if source == "BigQuery":
        return f"`{PROJECT}.analytics.{name}`"
    return f"analytics.{name}"


@st.cache_data(ttl=300)
def run_query(sql, source):
    if source == "BigQuery":
        from google.cloud import bigquery

        client = bigquery.Client(project=PROJECT)
        return client.query(sql).to_dataframe()

    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL

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
    return pd.read_sql(sql, engine)


prices = run_query(
    f"SELECT coin, price_usd, price_time FROM {table('stg_crypto_prices')} ORDER BY price_time",
    source,
)
prices["price_usd"] = prices["price_usd"].astype(float)

summary = run_query(
    f"SELECT * FROM {table('daily_price_summary')} ORDER BY price_date DESC, coin",
    source,
)
summary["price_date"] = pd.to_datetime(summary["price_date"]).dt.date

coin = st.selectbox("Coin", sorted(prices["coin"].unique()))
selected = prices[prices["coin"] == coin]

st.subheader(f"{coin} price (USD)")
chart = (
    alt.Chart(selected)
    .mark_line(point=True)
    .encode(
        x=alt.X("price_time:T", title="Time"),
        y=alt.Y("price_usd:Q", title="Price (USD)", scale=alt.Scale(zero=False)),
        tooltip=["price_time:T", "price_usd:Q"],
    )
    .properties(height=350)
)
st.altair_chart(chart)

st.subheader("Daily summary")
st.dataframe(summary)