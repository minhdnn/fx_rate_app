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
                        # Translate common Vietnamese gold terms to English
                        english_name = translate_gold_name(name)
                        
                        rates.append({
                            'type': 'gold',
                            'category': 'domestic',
                            'name': english_name,
                            'original_name': name,  # Keep original for reference
                            'key': key,
                            'buy': buy,
                            'sell': sell,
                            'unit': 'VND/tael',  # Use 'tael' instead of 'chỉ'
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
                        english_name = translate_gold_name(name)
                        
                        rates.append({
                            'type': 'gold',
                            'category': 'international',
                            'name': english_name,
                            'original_name': name,
                            'key': key,
                            'buy': buy,
                            'sell': sell,
                            'unit': 'USD/oz' if 'USD' in name else 'VND/tael',
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
                        english_name = translate_gold_name(name)
                        
                        # Determine unit based on price range
                        unit = 'VND/tael' if sell > 1000 else 'VND/gram'
                        if 'thousand' in english_name.lower():
                            unit = 'VND x1000/tael'
                        
                        rates.append({
                            'type': 'jewelry',
                            'category': 'gold_jewelry',
                            'name': english_name,
                            'original_name': name,
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

def translate_gold_name(vietnamese_name):
    """Translate Vietnamese gold names to English"""
    translations = {
        # Common gold types
        'Vàng SJC': 'SJC Gold',
        'Vàng DOJI': 'DOJI Gold',
        'Vàng PNJ': 'PNJ Gold',
        'Vàng Bảo Tín': 'Bao Tin Gold',
        'Vàng 24k': '24k Gold',
        'Vàng 18k': '18k Gold',
        'Vàng 14k': '14k Gold',
        'Vàng 10k': '10k Gold',
        'Vàng 9999': '9999 Gold',
        'Vàng trang sức': 'Jewelry Gold',
        'Vàng nhẫn': 'Ring Gold',
        'Vàng dây chuyền': 'Necklace Gold',
        'Vàng lắc': 'Bracelet Gold',
        'Vàng bông tai': 'Earring Gold',
        
        # Units and descriptors
        'chỉ': 'tael',
        'gram': 'gram',
        'nghìn': 'thousand',
        'triệu': 'million',
        'tỷ': 'billion',
        'mua': 'buy',
        'bán': 'sell',
        'giá': 'price',
        'hôm nay': 'today',
        'cập nhật': 'updated',
        
        # International terms
        'USD': 'USD',
        'Ounce': 'Ounce',
        'Troy Ounce': 'Troy Ounce',
        'Spot': 'Spot',
        'Future': 'Future',
        'London': 'London',
        'New York': 'New York',
        'Comex': 'Comex',
        'Loco London': 'Loco London',
        
        # Common patterns
        'Vàng miếng': 'Gold Bar',
        'Vàng lá': 'Gold Leaf',
        'Vàng nữ trang': 'Women\'s Jewelry',
        'Vàng nam': 'Men\'s Gold',
        'Vàng trẻ em': 'Children\'s Gold',
        'Kim cương': 'Diamond',
        'Bạc': 'Silver',
        'Bạch kim': 'Platinum'
    }
    
    # Start with the original name
    result = vietnamese_name
    
    # Apply translations
    for vn_term, en_term in translations.items():
        result = result.replace(vn_term, en_term)
    
    # Clean up extra spaces and formatting
    result = ' '.join(result.split())
    
    return result

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
                name = translate_gold_name(row.get('Name', ''))
                charts.append({
                    'type': 'international_chart',
                    'name': name,
                    'original_name': row.get('Name', ''),
                    'key': row.get('Key', ''),
                    'url': row.get('Url', '')
                })
        
        # Get Domestic Gold Chart
        gp_chart = root.find('GPChart')
        if gp_chart is not None:
            for row in gp_chart.findall('Row'):
                name = translate_gold_name(row.get('Name', ''))
                charts.append({
                    'type': 'domestic_chart',
                    'name': name,
                    'original_name': row.get('Name', ''),
                    'key': row.get('Key', ''),
                    'url': row.get('Url', '')
                })
        
        return charts
        
    except Exception as e:
        logger.error(f"Error fetching gold charts: {e}")
        return []
