\# Crypto Price ETL Pipeline



A small data engineering project that collects cryptocurrency prices from a public API, cleans them, and stores them in PostgreSQL.



\## Architecture



CoinGecko API -> Python (requests, pandas) -> PostgreSQL (running in Docker)



\## What it does



\- \*\*Extract:\*\* fetches Bitcoin, Ethereum and Solana prices (USD) from the CoinGecko API

\- \*\*Transform:\*\* converts the response into a pandas DataFrame and turns Unix timestamps into UTC datetimes

\- \*\*Load:\*\* inserts the rows into a `crypto\_prices` table in PostgreSQL



The pipeline is idempotent: the primary key `(coin, price\_time)` together with `ON CONFLICT DO NOTHING` means running it multiple times never creates duplicate rows.



\## Tech stack



Python, pandas, SQLAlchemy, PostgreSQL, Docker



\## How to run



1\. Install Python and Docker Desktop.

2\. Create a virtual environment and install dependencies:



```

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

```



3\. Start PostgreSQL:



```

docker compose up -d

```



4\. Run the pipeline:



```

python pipeline.py

```



\## Example query



```sql

SELECT coin,

&#x20;      price\_time,

&#x20;      price\_usd,

&#x20;      price\_usd - LAG(price\_usd) OVER (PARTITION BY coin ORDER BY price\_time) AS change

FROM crypto\_prices

ORDER BY coin, price\_time;

```



\## Roadmap



\- Transformations with dbt

\- Scheduling with Apache Airflow

\- Dashboard for the price history

