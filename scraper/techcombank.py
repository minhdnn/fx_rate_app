# scraper/techcombank.py

import requests
from bs4 import BeautifulSoup

def get_techcombank_rates():
    url = "https://techcombank.com/cong-cu-tien-ich/ty-gia"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rates = []

    if not table:
        raise Exception("Exchange rate table not found")

    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            currency = cols[0].text.strip()
            buy = float(cols[1].text.replace(",", "").strip())
            sell = float(cols[3].text.replace(",", "").strip())
            rates.append({
                "bank": "Techcombank",
                "currency": currency,
                "buy": buy,
                "sell": sell
            })

    return rates
