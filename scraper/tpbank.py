import requests
from bs4 import BeautifulSoup
import json
import re

def get_tpbank_rates():
    """Scrape exchange rates from TPBank"""
    url = "https://tpb.vn/cong-cu-tinh-toan/ty-gia-ngoai-te"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        # Try to find API endpoint or JSON data
        api_match = re.search(r'/api/[^"\']*exchange[^"\']*|/api/[^"\']*rate[^"\']*', res.text)
        if api_match:
            api_url = api_match.group(0)
            if not api_url.startswith('http'):
                api_url = 'https://tpb.vn' + api_url
            
            try:
                api_res = session.get(api_url, headers=headers, timeout=10)
                if api_res.status_code == 200:
                    api_data = api_res.json()
                    return parse_tpbank_api_data(api_data)
            except:
                pass
        
        # Parse HTML
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Look for exchange rate table or data
        table = soup.find("table", class_=re.compile(r".*rate.*|.*tygia.*", re.I))
        if not table:
            table = soup.find("div", class_=re.compile(r".*rate.*|.*tygia.*", re.I))
        
        if not table:
            # Try to find script with data
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and any(currency in script.string for currency in ['USD', 'EUR', 'JPY']):
                    return parse_tpbank_script(script.string)
            
            print("Could not find exchange rate data for TPBank")
            return []
            
        target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
        rates = []
        
        # Handle different table structures
        rows = table.find_all("tr")
        if not rows:
            # Maybe it's a div-based layout
            rate_items = table.find_all("div", class_=re.compile(r".*item.*|.*row.*", re.I))
            return parse_tpbank_divs(rate_items, target_currencies)
        
        for row in rows[1:]:  # Skip header
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
                # Extract rates - TPBank might have different column structure
                buy_text = ""
                sell_text = ""
                
                # Try different column combinations
                for i in range(1, min(len(cols), 4)):
                    text = cols[i].get_text().replace(',', '').replace('.', '').strip()
                    if text and text.replace('.', '').replace(',', '').isdigit():
                        if not buy_text:
                            buy_text = text
                        elif not sell_text:
                            sell_text = text
                            break
                
                buy = float(buy_text) if buy_text else None
                sell = float(sell_text) if sell_text else None
                
                if buy and sell:
                    rates.append({
                        'bank': 'TPBank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                print(f"Error parsing TPBank rate for {currency}: {e}")
                continue
                
        return rates
        
    except requests.RequestException as e:
        print(f"Error fetching TPBank rates: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in TPBank scraper: {e}")
        return []

def parse_tpbank_api_data(data):
    """Parse exchange rates from API data"""
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []
    
    try:
        # Handle different API response structures
        rate_data = data
        
        if 'data' in data:
            rate_data = data['data']
        elif 'result' in data:
            rate_data = data['result']
        elif 'rates' in data:
            rate_data = data['rates']
            
        if isinstance(rate_data, list):
            for item in rate_data:
                currency = item.get('currency', '').upper()
                if currency in target_currencies:
                    rates.append({
                        'bank': 'TPBank',
                        'currency': currency,
                        'buy': float(item.get('buyRate', item.get('buy', 0))),
                        'sell': float(item.get('sellRate', item.get('sell', 0)))
                    })
        elif isinstance(rate_data, dict):
            for currency in target_currencies:
                if currency in rate_data:
                    item = rate_data[currency]
                    rates.append({
                        'bank': 'TPBank',
                        'currency': currency,
                        'buy': float(item.get('buy', item.get('buyRate', 0))),
                        'sell': float(item.get('sell', item.get('sellRate', 0)))
                    })
        
    except Exception as e:
        print(f"Error parsing TPBank API data: {e}")
    
    return rates

def parse_tpbank_script(script_content):
    """Parse exchange rates from script content"""
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    rates = []
    
    try:
        # Look for JSON-like structures
        json_match = re.search(r'\{[^{}]*(?:"USD"|"EUR"|"JPY"|"CNY")[^{}]*\}', script_content)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                return parse_tpbank_api_data(data)
            except:
                pass
        
        # Look for individual currency patterns
        for currency in target_currencies:
            # Pattern for "USD": {"buy": 24000, "sell": 24500}
            pattern = rf'"{currency}".*?"buy"\s*:\s*([0-9,.]+).*?"sell"\s*:\s*([0-9,.]+)'
            match = re.search(pattern, script_content, re.IGNORECASE | re.DOTALL)
            
            if match:
                try:
                    buy = float(match.group(1).replace(',', ''))
                    sell = float(match.group(2).replace(',', ''))
                    rates.append({
                        'bank': 'TPBank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                except ValueError:
                    continue
    
    except Exception as e:
        print(f"Error parsing TPBank script: {e}")
    
    return rates

def parse_tpbank_divs(rate_items, target_currencies):
    """Parse exchange rates from div-based layout"""
    rates = []
    
    try:
        for item in rate_items:
            text = item.get_text().upper()
            
            currency = None
            for target in target_currencies:
                if target in text:
                    currency = target
                    break
                    
            if not currency:
                continue
                
            # Extract numbers from the text
            numbers = re.findall(r'[0-9,]+(?:\.[0-9]+)?', item.get_text())
            numbers = [float(n.replace(',', '')) for n in numbers if n.replace(',', '').replace('.', '').isdigit()]
            
            if len(numbers) >= 2:
                rates.append({
                    'bank': 'TPBank',
                    'currency': currency,
                    'buy': numbers[0],
                    'sell': numbers[1]
                })
                
    except Exception as e:
        print(f"Error parsing TPBank divs: {e}")
    
    return rates
