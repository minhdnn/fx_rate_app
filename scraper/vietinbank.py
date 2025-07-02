import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

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
        table = soup.find("table", class_="table-tygia") or soup.find("table", {"id": "tblExchangeRate"})
        
        if not table:
            # Try alternative selectors
            table = soup.find("div", class_="exchange-rate-table")
            if table:
                table = table.find("table")
        
        if not table:
            logger.warning("Could not find exchange rate table for Vietinbank")
            return []
        
        rows = table.find_all("tr")[1:]  # Skip header row
        target_currencies = ['USD', 'EUR', 'JPY', 'CNY']
        rates = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            # Currency is usually in first column
            currency_cell = cols[0].text.strip()
            
            # Clean currency code (remove extra text)
            currency = None
            for target in target_currencies:
                if target in currency_cell.upper():
                    currency = target
                    break
            
            if not currency:
                continue

            try:
                # Vietinbank typically has: Currency | Cash Buy | Cash Sell | Transfer Buy | Transfer Sell
                # We'll use transfer rates (columns 3 and 4) or cash rates (columns 1 and 2) as fallback
                
                if len(cols) >= 5:  # Has both cash and transfer rates
                    buy = float(cols[3].text.replace(',', '').replace('-', '0').strip())
                    sell = float(cols[4].text.replace(',', '').replace('-', '0').strip())
                elif len(cols) >= 3:  # Only cash rates
                    buy = float(cols[1].text.replace(',', '').replace('-', '0').strip())
                    sell = float(cols[2].text.replace(',', '').replace('-', '0').strip())
                else:
                    continue
                
                if buy > 0 and sell > 0:  # Valid rates
                    rates.append({
                        'bank': 'Vietinbank',
                        'currency': currency,
                        'buy': buy,
                        'sell': sell
                    })
                    
            except (ValueError, AttributeError) as e:
                logger.debug(f"Error parsing Vietinbank rate for {currency}: {e}")
                continue

        logger.info(f"Successfully scraped {len(rates)} rates from Vietinbank")
        return rates
        
    except requests.RequestException as e:
        logger.error(f"Error fetching Vietinbank rates: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error scraping Vietinbank: {e}")
        return []
