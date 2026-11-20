select
    coin,
    price_usd,
    price_time,
    fetched_at,
    {% if target.type == 'bigquery' %}
    date(price_time, 'UTC') as price_date
    {% else %}
    cast(price_time at time zone 'UTC' as date) as price_date
    {% endif %}
from {{ source('crypto', 'crypto_prices') }}