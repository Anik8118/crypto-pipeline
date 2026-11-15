select
    coin,
    price_usd,
    price_time,
    fetched_at,
    cast(price_time at time zone 'UTC' as date) as price_date
from {{ source('crypto', 'crypto_prices') }}