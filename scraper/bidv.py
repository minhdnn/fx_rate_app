# scraper/bidv.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def get_bidv_rates():
    """
    Trả về list dict dạng:
    {'bank': 'BIDV', 'currency': 'USD', 'buy': 23520.0, 'sell': 23640.0}
    """
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    # 1. Mở trang bằng Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://bidv.com.vn/vn/ty-gia-ngoai-te", timeout=60_000)
        html = page.content()
        browser.close()

    # 2. Dùng BeautifulSoup để parse
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")          # selector chung → đủ cho BIDV
    if not table:
        return rates                    # Trang đổi cấu trúc → trả list rỗng

    rows = table.find_all("tr")[1:]     # bỏ dòng tiêu đề

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        currency = cols[0].text.strip()
        if currency not in target_currencies:
            continue

        try:
            buy  = float(cols[1].text.strip().replace(',', ''))
            sell = float(cols[3].text.strip().replace(',', ''))
        except ValueError:
            continue

        rates.append({
            'bank'    : 'BIDV',
            'currency': currency,
            'buy'     : buy,
            'sell'    : sell,
        })

    return rates
