import requests
from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)

def get_techcombank_rates():
    """Scrape exchange rates from Techcombank"""
    url = "https://techcombank.com/cong-cu-tien-ich/ty-gia"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Try to find API endpoint or data in script tags
        script_tags = soup.find_all('script')
        rates = []
        
        # Look for JSON data in script tags
        for script in script_tags:
            if script.string and 'exchange' in script.string.lower():
                try:
                    # Try to extract JSON data
                    script_content = script.string
                    if 'exchangeRate' in script_content or 'rates' in script_content:
                        # This might contain the exchange rate data
                        pass
                except:
                    continue
        
        # Fallback: Try to find table in HTML
        table = soup.find("table", class_="exchange-rate") or soup.find("div", class_="exchange-rates")
        
        if table and table.name == 'div':
            table = table.find("table")
        
        if not table:
            # Try alternative approach - look for API calls
            try:
                # Techcombank might use AJAX calls, try to find the API endpoint
                api_url = "https://techcombank.com/api/exchange-rates"  # Hypothetical API endpoint
                api_res = session.get(api_url, headers=headers, timeout=10)
                if api_res.status_code == 200:
                    data = api_res.json()
                    return parse_techcombank_api_data(data)
            except:
                pass
            
            logger.warning("Could not find exchange rate data for Techcombank")
            return []

        rows = table.find_all("tr")[1:]  # Skip header
        target_currencies = ['USD', 'EUR', 'JPY', 'CNY']

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
                # Techcombank format: Currency | Buy | Sell
                buy_text = cols[1].text.replace(',', '').replace('-', '0').strip()
                sell_text = cols[2].text.replace(',', '').replace('-', '0').strip()
                
                buy = float(buy_text)
                sell = float(sell_text)
                
                if buy > 0 and sell > 0:
                    rates.append({
                        'bank': 'Techcombank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                logger.debug(f"Error parsing Techcombank rate for {currency}: {e}")
                continue

        logger.info(f"Successfully scraped {len(rates)} rates from Techcombank")
        return rates
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Techcombank rates: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error scraping Techcombank: {e}")
        return []

def parse_techcombank_api_data(data):
    """Parse API response data from Techcombank"""
    rates = []
    target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
    
    try:
        # This would depend on the actual API response structure
        if isinstance(data, dict) and 'rates' in data:
            for rate_data in data['rates']:
                currency = rate_data.get('currency', '').upper()
                if currency in target_currencies:
                    rates.append({
                        'bank': 'Techcombank',
                        'currency': currency,
                        'buy': float(rate_data.get('buy', 0)),
                        'sell': float(rate_data.get('sell', 0))
                    })
    except Exception as e:
        logger.error(f"Error parsing Techcombank API data: {e}")
    
    return rates
