import requests
import xml.etree.ElementTree as ET

def get_vcb_rates():
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
    res = requests.get(url)
    root = ET.fromstring(res.content)
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []

    for item in root.findall('Exrate'):
        currency = item.get('CurrencyCode')
        if currency in target_currencies:
            try:
                buy = float(item.get('Transfer').replace(',', ''))
                sell = float(item.get('Sell').replace(',', ''))
                rates.append({
                    'bank': 'VCB',
                    'currency': currency,
                    'buy': buy,
                    'sell': sell
                })
            except:
                continue
    return rates
