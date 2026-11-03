import requests

URL = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": "bitcoin,ethereum,solana",
    "vs_currencies": "usd",
    "include_last_updated_at": "true",
}

response = requests.get(URL, params=params, timeout=30)
response.raise_for_status()
data = response.json()

print(data)