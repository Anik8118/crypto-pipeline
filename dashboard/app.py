import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://de_user:de_pass@localhost:5432/crypto")

st.title("Crypto Price Dashboard")

prices = pd.read_sql(
    "SELECT coin, price_usd, price_time FROM analytics.stg_crypto_prices ORDER BY price_time",
    engine,
)
prices["price_usd"] = prices["price_usd"].astype(float)

summary = pd.read_sql(
    "SELECT * FROM analytics.daily_price_summary ORDER BY price_date DESC, coin",
    engine,
)

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