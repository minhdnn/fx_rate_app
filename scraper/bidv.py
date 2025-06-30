import requests
from bs4 import BeautifulSoup

def get_bidv_rates():
    url = "https://bidv.com.vn/vn/ty-gia-ngoai-te"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table")
    rows = table.find_all("tr")[1:]  # Skip header
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        currency = cols[0].text.strip()
        if currency not in target_currencies:
            continue

        try:
            buy = float(cols[1].text.replace(',', ''))
            sell = float(cols[3].text.replace(',', ''))
        except:
            continue

        rates.append({
            'bank': 'BIDV',
            'currency': currency,
            'buy': buy,
            'sell': sell
        })

    return rates
