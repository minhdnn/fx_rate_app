import requests
from bs4 import BeautifulSoup

def get_bidv_rates():
    url = "https://www.bidv.com.vn/vn/ty-gia/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    rates = {}

    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            cells = row.find_all("td")
            if len(cells) >= 4:
                currency = cells[0].get_text(strip=True)
                buy = cells[1].get_text(strip=True).replace(",", "")
                transfer = cells[2].get_text(strip=True).replace(",", "")
                sell = cells[3].get_text(strip=True).replace(",", "")
                rates[currency] = {
                    "buy": float(buy),
                    "transfer": float(transfer),
                    "sell": float(sell)
                }

    return rates
