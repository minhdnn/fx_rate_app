# scraper/vietinbank.py
import requests
from bs4 import BeautifulSoup

def get_vietinbank_rates():
    url = "https://www.vietinbank.vn/ca-nhan/ty-gia-khcn"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers, timeout=15)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")

    if not table:
        raise Exception("Cannot find exchange rate table")

    rows = table.find_all("tr")[1:]
    rates = []

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
