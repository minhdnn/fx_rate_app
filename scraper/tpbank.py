# scraper/tpbank.py
import requests
import time

def get_tpbank_rates():
    url = "https://api.tpb.vn/common/exchangeRate/getExchangeRates"
    retries = 3
    delay = 3

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
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
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise Exception("TPBank API timed out after multiple attempts")
