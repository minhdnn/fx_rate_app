# scraper/vietinbank.py

import requests
from bs4 import BeautifulSoup

def get_vietinbank_rates():
    url = "https://www.vietinbank.vn/ca-nhan/ty-gia-khcn"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rates = []

    if not table:
        raise Exception("Exchange rate table not found")

    rows = table.find_all("tr")[1:]  # Skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            currency = cols[0].text.strip()
            buy = float(cols[1].text.replace(",", "").strip())
            sell = float(cols[3].text.replace(",", "").strip())
            rates.append({
                "bank": "Vietinbank",
                "currency": currency,
                "buy": buy,
                "sell": sell
            })

    return rates
