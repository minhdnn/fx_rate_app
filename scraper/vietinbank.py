from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def get_vietinbank_rates():
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.vietinbank.vn/ca-nhan/ty-gia-khcn", timeout=60000)
        page.wait_for_selector("table")  # Ensure table is loaded
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]  # Skip header

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
        except:
            continue

        rates.append({
            'bank': 'Vietin',
            'currency': currency,
            'buy': buy,
            'sell': sell
        })

    return rates
