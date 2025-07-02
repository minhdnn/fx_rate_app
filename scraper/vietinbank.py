import requests
from bs4 import BeautifulSoup
import re

def get_vietinbank_rates():
    """Scrape exchange rates from Vietinbank"""
    url = "https://www.vietinbank.vn/ca-nhan/ty-gia-khcn"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Find the exchange rate table
        table = soup.find("table", class_="tbl-tygia") or soup.find("div", class_="tygia-content")
        if not table:
            # Try alternative selectors
            table = soup.find("table", {"id": re.compile(r".*tygia.*", re.I)})
        
        if not table:
            print("Could not find exchange rate table for Vietinbank")
            return []
            
        target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
        rates = []
        
        # Look for table rows
        rows = table.find_all("tr")
        
        for row in rows[1:]:  # Skip header row
            cols = row.find_all(["td", "th"])
            if len(cols) < 4:
                continue
                
            # Extract currency code (usually first column)
            currency_text = cols[0].get_text().strip()
            
            # Extract currency code from text (handle cases like "USD - Đô la Mỹ")
            currency = None
            for target in target_currencies:
                if target in currency_text.upper():
                    currency = target
                    break
                    
            if not currency:
                continue
                
            try:
                # Try to find buy and sell rates (usually columns 2 and 3 or 3 and 4)
                buy_text = cols[1].get_text().replace(',', '').replace('.', '').strip()
                sell_text = cols[2].get_text().replace(',', '').replace('.', '').strip()
                
                # Handle different formats
                buy = float(buy_text) if buy_text and buy_text.replace('.', '').replace(',', '').isdigit() else None
                sell = float(sell_text) if sell_text and sell_text.replace('.', '').replace(',', '').isdigit() else None
                
                # If rates are in different columns, try alternative positions
                if not buy or not sell:
                    if len(cols) > 3:
                        buy_text = cols[2].get_text().replace(',', '').replace('.', '').strip()
                        sell_text = cols[3].get_text().replace(',', '').replace('.', '').strip()
                        buy = float(buy_text) if buy_text and buy_text.replace('.', '').replace(',', '').isdigit() else None
                        sell = float(sell_text) if sell_text and sell_text.replace('.', '').replace(',', '').isdigit() else None
                
                if buy and sell:
                    rates.append({
                        'bank': 'Vietinbank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                print(f"Error parsing Vietinbank rate for {currency}: {e}")
                continue
                
        return rates
        
    except requests.RequestException as e:
        print(f"Error fetching Vietinbank rates: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in Vietinbank scraper: {e}")
        return []
