import requests
from bs4 import BeautifulSoup

def get_vietinbank_rates():
    url = "https://www.vietinbank.vn/ca-nhan/ty-gia-khcn"
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.find("table")
        if not table:
            print("Không tìm thấy bảng tỷ giá trên trang Vietinbank.")
            return []

        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            currency = cols[0].text.strip()
            if currency not in target_currencies:
                continue

            try:
                buy = float(cols[2].text.replace(',', '').strip())
                sell = float(cols[4].text.replace(',', '').strip())
                rates.append({
                    'bank': 'Vietin',
                    'currency': currency,
                    'buy': buy,
                    'sell': sell
                })
            except ValueError:
                continue

    except Exception as e:
        print(f"Lỗi khi lấy tỷ giá Vietinbank: {e}")

    return rates
