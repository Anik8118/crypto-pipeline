select
    coin,
    price_date,
    count(*) as readings,
    round(avg(price_usd), 2) as avg_price,
    min(price_usd) as min_price,
    max(price_usd) as max_price
from {{ ref('stg_crypto_prices') }}
group by coin, price_date