# scraper/tpbank.py

import requests

def get_tpbank_rates():
    url = "https://api.tpb.vn/common/exchangeRate/getExchangeRates"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    rates = []

    for item in data.get("data", []):
        currency = item.get("currencyCode")
        if not currency:
            continue

        buy = float(item.get("buy", 0))
        sell = float(item.get("sell", 0))

        rates.append({
            "bank": "TP Bank",
            "currency": currency,
            "buy": buy,
            "sell": sell
        })

    return rates
