import requests
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

def get_doji_gold_rates():
    """Scrape gold prices from DOJI API"""
    url = "http://giavang.doji.vn/api/giavang/?api_key=258fbd2a72ce8481089d88c678e9fe4f"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse XML response
        root = ET.fromstring(response.content)
        rates = []
        
        # Parse DGPlist (Domestic Gold Prices)
        dgp_list = root.find('DGPlist')
        if dgp_list is not None:
            datetime_element = dgp_list.find('DateTime')
            last_updated = datetime_element.text if datetime_element is not None else "Unknown"
            
            for row in dgp_list.findall('Row'):
                name = row.get('Name', '')
                key = row.get('Key', '')
                sell_text = row.get('Sell', '0').replace(',', '').replace('-', '0')
                buy_text = row.get('Buy', '0').replace(',', '').replace('-', '0')
                
                try:
                    sell = float(sell_text) if sell_text and sell_text != '0' else 0
                    buy = float(buy_text) if buy_text and buy_text != '0' else 0
                    
                    if sell > 0 or buy > 0:  # Only include if we have valid prices
                        rates.append({
                            'type': 'gold',
                            'category': 'domestic',
                            'name': name,
                            'key': key,
                            'buy': buy,
                            'sell': sell,
                            'unit': 'VND/chỉ',
                            'last_updated': last_updated
                        })
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse gold price for {name}")
                    continue
        
        # Parse IGPList (International Gold Prices)
        igp_list = root.find('IGPList')
        if igp_list is not None:
            datetime_element = igp_list.find('DateTime')
            last_updated = datetime_element.text if datetime_element is not None else "Unknown"
            
            for row in igp_list.findall('Row'):
                name = row.get('Name', '')
                key = row.get('Key', '')
                sell_text = row.get('Sell', '0').replace(',', '').replace('-', '0')
                buy_text = row.get('Buy', '0').replace(',', '').replace('-', '0')
                
                try:
                    sell = float(sell_text) if sell_text and sell_text != '0' else 0
                    buy = float(buy_text) if buy_text and buy_text != '0' else 0
                    
                    if sell > 0 or buy > 0:
                        rates.append({
                            'type': 'gold',
                            'category': 'international',
                            'name': name,
                            'key': key,
                            'buy': buy,
                            'sell': sell,
                            'unit': 'VND' if 'VND' in name else 'USD',
                            'last_updated': last_updated
                        })
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse international gold price for {name}")
                    continue
        
        # Parse JewelryList (Jewelry Prices)
        jewelry_list = root.find('JewelryList')
        if jewelry_list is not None:
            datetime_element = jewelry_list.find('DateTime')
            last_updated = datetime_element.text if datetime_element is not None else "Unknown"
            
            for row in jewelry_list.findall('Row'):
                name = row.get('Name', '')
                key = row.get('Key', '')
                sell_text = row.get('Sell', '0').replace(',', '').replace('-', '0')
                buy_text = row.get('Buy', '0').replace(',', '').replace('-', '0')
                
                try:
                    sell = float(sell_text) if sell_text and sell_text != '0' else 0
                    buy = float(buy_text) if buy_text and buy_text != '0' else 0
                    
                    if sell > 0 or buy > 0:
                        # Determine unit based on price range
                        unit = 'VND/chỉ' if sell > 1000 else 'VND/gram'
                        if 'nghìn' in name.lower():
                            unit = 'VND x1000/chỉ'
                        
                        rates.append({
                            'type': 'jewelry',
                            'category': 'gold_jewelry',
                            'name': name,
                            'key': key,
                            'buy': buy,
                            'sell': sell,
                            'unit': unit,
                            'last_updated': last_updated
                        })
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse jewelry price for {name}")
                    continue
        
        logger.info(f"Successfully fetched {len(rates)} gold/jewelry prices from DOJI")
        return rates
        
    except requests.RequestException as e:
        logger.error(f"Error fetching DOJI gold rates: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error parsing DOJI XML response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in DOJI scraper: {e}")
        return []

def get_gold_charts():
    """Get gold chart URLs from DOJI API"""
    url = "http://giavang.doji.vn/api/giavang/?api_key=258fbd2a72ce8481089d88c678e9fe4f"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        charts = []
        
        # Get International Gold Chart
        igp_chart = root.find('IGPChart')
        if igp_chart is not None:
            for row in igp_chart.findall('Row'):
                charts.append({
                    'type': 'international_chart',
                    'name': row.get('Name', ''),
                    'key': row.get('Key', ''),
                    'url': row.get('Url', '')
                })
        
        # Get Domestic Gold Chart
        gp_chart = root.find('GPChart')
        if gp_chart is not None:
            for row in gp_chart.findall('Row'):
                charts.append({
                    'type': 'domestic_chart',
                    'name': row.get('Name', ''),
                    'key': row.get('Key', ''),
                    'url': row.get('Url', '')
                })
        
        return charts
        
    except Exception as e:
        logger.error(f"Error fetching gold charts: {e}")
        return []
