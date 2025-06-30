import httpx
from bs4 import BeautifulSoup

def get_bidv_rates():
    url = "https://www.bidv.com.vn/vn/ty-gia/"
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    try:
        with httpx.Client(verify=False, timeout=30.0) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html = response.text
    except Exception as e:
        print(f"Lỗi khi truy cập BIDV: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        print("Không tìm thấy bảng tỉ giá BIDV")
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
            buy = float(cols[1].text.replace(',', '').strip())
            sell = float(cols[3].text.replace(',', '').strip())
            rates.append({
                'bank': 'BIDV',
                'currency': currency,
                'buy': buy,
                'sell': sell
            })
        except ValueError:
            continue

    return rates
