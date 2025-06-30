import requests
from bs4 import BeautifulSoup

def get_agribank_rates():
    url = "https://www.agribank.com.vn/vn/ty-gia"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table", class_="table")  # class name may vary
    rows = table.find_all("tr")[1:]  # Skip header

    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        currency = cols[0].text.strip()
        if currency not in target_currencies:
            continue

        try:
            buy = float(cols[1].text.replace(',', '').strip())
            sell = float(cols[3].text.replace(',', '').strip())
        except:
            continue

        rates.append({
            'bank': 'Agribank',
            'currency': currency,
            'buy': buy,
            'sell': sell
        })

    return rates
