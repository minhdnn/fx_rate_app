import requests
from bs4 import BeautifulSoup
import json
import re

def get_techcombank_rates():
    """Scrape exchange rates from Techcombank"""
    url = "https://techcombank.com/cong-cu-tien-ich/ty-gia"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        # Try to find JSON data first (many modern sites use this)
        json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', res.text)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return parse_techcombank_json(data)
            except:
                pass
        
        # Fallback to HTML parsing
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Look for exchange rate table
        table = soup.find("table") or soup.find("div", class_=re.compile(r".*rate.*|.*tygia.*", re.I))
        
        if not table:
            # Try to find script tags with rate data
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and ("USD" in script.string or "EUR" in script.string):
                    return parse_techcombank_script(script.string)
            
            print("Could not find exchange rate data for Techcombank")
            return []
            
        target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
        rates = []
        
        rows = table.find_all("tr")
        
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 3:
                continue
                
            currency_text = cols[0].get_text().strip().upper()
            
            currency = None
            for target in target_currencies:
                if target in currency_text:
                    currency = target
                    break
                    
            if not currency:
                continue
                
            try:
                # Extract buy and sell rates
                buy_text = cols[1].get_text().replace(',', '').replace('.', '').strip()
                sell_text = cols[2].get_text().replace(',', '').replace('.', '').strip()
                
                buy = float(buy_text) if buy_text and buy_text.replace('.', '').replace(',', '').isdigit() else None
                sell = float(sell_text) if sell_text and sell_text.replace('.', '').replace(',', '').isdigit() else None
                
                if buy and sell:
                    rates.append({
                        'bank': 'Techcombank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                print(f"Error parsing Techcombank rate for {currency}: {e}")
                continue
                
        return rates
        
    except requests.RequestException as e:
        print(f"Error fetching Techcombank rates: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in Techcombank scraper: {e}")
        return []

def parse_techcombank_json(data):
    """Parse exchange rates from JSON data"""
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []
    
    try:
        # Navigate through the JSON structure to find rates
        # This structure may vary, so we'll try common patterns
        rate_data = None
        
        if 'exchangeRates' in data:
            rate_data = data['exchangeRates']
        elif 'rates' in data:
            rate_data = data['rates']
        elif 'data' in data and isinstance(data['data'], dict):
            if 'rates' in data['data']:
                rate_data = data['data']['rates']
        
        if rate_data and isinstance(rate_data, list):
            for item in rate_data:
                if 'currency' in item and item['currency'] in target_currencies:
                    rates.append({
                        'bank': 'Techcombank',
                        'currency': item['currency'],
                        'buy': float(item.get('buy', 0)),
                        'sell': float(item.get('sell', 0))
                    })
        
    except Exception as e:
        print(f"Error parsing Techcombank JSON: {e}")
    
    return rates

def parse_techcombank_script(script_content):
    """Parse exchange rates from script content"""
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []
    
    try:
        # Look for patterns like "USD": {"buy": 24000, "sell": 24500}
        for currency in target_currencies:
            pattern = rf'"{currency}".*?"buy"\s*:\s*([0-9,.]+).*?"sell"\s*:\s*([0-9,.]+)'
            match = re.search(pattern, script_content, re.IGNORECASE | re.DOTALL)
            
            if match:
                try:
                    buy = float(match.group(1).replace(',', ''))
                    sell = float(match.group(2).replace(',', ''))
                    rates.append({
                        'bank': 'Techcombank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                except ValueError:
                    continue
    
    except Exception as e:
        print(f"Error parsing Techcombank script: {e}")
    
    return rates
