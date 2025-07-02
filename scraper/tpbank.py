import requests
from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)

def get_tpbank_rates():
    """Scrape exchange rates from TP Bank"""
    url = "https://tpb.vn/cong-cu-tinh-toan/ty-gia-ngoai-te"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Referer': 'https://tpb.vn/',
        }
        
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # TPBank might use dynamic loading, check for API calls or JSON data
        rates = []
        
        # Look for exchange rate data in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and ('exchange' in script.string.lower() or 'tygia' in script.string.lower()):
                try:
                    # Try to find JSON data
                    script_content = script.string
                    # Look for patterns like exchangeRates = {...} or similar
                    if 'exchangeRate' in script_content or 'rates' in script_content:
                        # Parse potential JSON data
                        lines = script_content.split('\n')
                        for line in lines:
                            if 'exchangeRate' in line or 'rates' in line:
                                try:
                                    # Extract JSON part
                                    start = line.find('{')
                                    end = line.rfind('}') + 1
                                    if start != -1 and end > start:
                                        json_str = line[start:end]
                                        data = json.loads(json_str)
                                        rates.extend(parse_tpbank_json_data(data))
                                except:
                                    continue
                except:
                    continue
        
        # If no data found in scripts, try HTML table
        if not rates:
            table = soup.find("table", class_="exchange-rate-table") or soup.find("div", class_="exchange-rate")
            
            if table and table.name == 'div':
                table = table.find("table")
            
            # Try more generic selectors
            if not table:
                tables = soup.find_all("table")
                for t in tables:
                    header_text = t.get_text().lower()
                    if 'usd' in header_text and ('mua' in header_text or 'buy' in header_text):
                        table = t
                        break
            
            if table:
                rates.extend(parse_tpbank_table(table))
        
        # Try API endpoint as fallback
        if not rates:
            try:
                api_url = "https://tpb.vn/api/exchange-rates"  # Hypothetical endpoint
                api_res = session.get(api_url, headers=headers, timeout=10)
                if api_res.status_code == 200:
                    data = api_res.json()
                    rates.extend(parse_tpbank_api_data(data))
            except:
                pass
        
        if not rates:
            logger.warning("Could not find exchange rate data for TP Bank")
        else:
            logger.info(f"Successfully scraped {len(rates)} rates from TP Bank")
        
        return rates
        
    except requests.RequestException as e:
        logger.error(f"Error fetching TP Bank rates: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error scraping TP Bank: {e}")
        return []

def parse_tpbank_table(table):
    """Parse exchange rates from HTML table"""
    rates = []
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    
    try:
        rows = table.find_all("tr")[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 3:
                continue

            currency_text = cols[0].text.strip().upper()
            
            # Find currency code
            currency = None
            for target in target_currencies:
                if target in currency_text:
                    currency = target
                    break
            
            if not currency:
                continue

            try:
                # TPBank format might be: Currency | Buy | Sell or Currency | Cash Buy | Cash Sell | Transfer Buy | Transfer Sell
                if len(cols) >= 5:  # Has both cash and transfer
                    buy = float(cols[3].text.replace(',', '').replace('-', '0').strip())
                    sell = float(cols[4].text.replace(',', '').replace('-', '0').strip())
                else:  # Simple format
                    buy = float(cols[1].text.replace(',', '').replace('-', '0').strip())
                    sell = float(cols[2].text.replace(',', '').replace('-', '0').strip())
                
                if buy > 0 and sell > 0:
                    rates.append({
                        'bank': 'TP Bank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                logger.debug(f"Error parsing TP Bank rate for {currency}: {e}")
                continue
    
    except Exception as e:
        logger.error(f"Error parsing TP Bank table: {e}")
    
    return rates

def parse_tpbank_json_data(data):
    """Parse JSON data from TP Bank"""
    rates = []
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    
    try:
        # This would depend on the actual JSON structure
        if isinstance(data, dict):
            if 'rates' in data:
                rates_data = data['rates']
            elif 'exchangeRates' in data:
                rates_data = data['exchangeRates']
            else:
                rates_data = data
            
            if isinstance(rates_data, list):
                for rate_item in rates_data:
                    currency = rate_item.get('currency', '').upper()
                    if currency in target_currencies:
                        buy = rate_item.get('buy') or rate_item.get('buyRate')
                        sell = rate_item.get('sell') or rate_item.get('sellRate')
                        
                        if buy and sell:
                            rates.append({
                                'bank': 'TP Bank',
                                'currency': currency,
                                'buy': float(buy),
                                'sell': float(sell)
                            })
            elif isinstance(rates_data, dict):
                for currency in target_currencies:
                    if currency in rates_data:
                        rate_data = rates_data[currency]
                        buy = rate_data.get('buy') or rate_data.get('buyRate')
                        sell = rate_data.get('sell') or rate_data.get('sellRate')
                        
                        if buy and sell:
                            rates.append({
                                'bank': 'TP Bank',
                                'currency': currency,
                                'buy': float(buy),
                                'sell': float(sell)
                            })
    
    except Exception as e:
        logger.error(f"Error parsing TP Bank JSON data: {e}")
    
    return rates

def parse_tpbank_api_data(data):
    """Parse API response from TP Bank"""
    return parse_tpbank_json_data(data)
