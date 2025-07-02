from flask import Flask, jsonify
from flask_cors import CORS
from scraper.vcb import get_vcb_rates
from scraper.agribank import get_agribank_rates
from scraper.vietinbank import get_vietinbank_rates
from scraper.techcombank import get_techcombank_rates
from scraper.tpbank import get_tpbank_rates
import logging
import concurrent.futures
from functools import wraps
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache
CACHE = {}
CACHE_DURATION = 300  # 5 minutes

def cache_result(duration=CACHE_DURATION):
    """Simple caching decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}_{args}_{kwargs}"
            now = time.time()
            
            if cache_key in CACHE:
                cached_data, timestamp = CACHE[cache_key]
                if now - timestamp < duration:
                    logger.info(f"Returning cached result for {func.__name__}")
                    return cached_data
            
            result = func(*args, **kwargs)
            CACHE[cache_key] = (result, now)
            return result
        return wrapper
    return decorator

@cache_result(300)  # Cache for 5 minutes
def aggregate_rates():
    """Aggregate rates from all banks using concurrent fetching"""
    scrapers = [
        ('VCB', get_vcb_rates),
        ('Agribank', get_agribank_rates),
        ('Vietinbank', get_vietinbank_rates),
        ('Techcombank', get_techcombank_rates),
        ('TPBank', get_tpbank_rates)
    ]
    
    all_rates = []
    failed_banks = []
    
    try:
        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all scraping tasks
            future_to_bank = {
                executor.submit(scraper_func): bank_name 
                for bank_name, scraper_func in scrapers
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_bank, timeout=30):
                bank_name = future_to_bank[future]
                try:
                    rates = future.result(timeout=10)
                    if rates:
                        all_rates.extend(rates)
                        logger.info(f"Successfully fetched {len(rates)} rates from {bank_name}")
                    else:
                        failed_banks.append(bank_name)
                        logger.warning(f"No rates returned from {bank_name}")
                except Exception as e:
                    failed_banks.append(bank_name)
                    logger.error(f"Error fetching rates from {bank_name}: {str(e)}")
                    
    except concurrent.futures.TimeoutError:
        logger.error("Timeout occurred while fetching rates")
    except Exception as e:
        logger.error(f"Error in concurrent rate fetching: {str(e)}")
    
    if failed_banks:
        logger.warning(f"Failed to fetch rates from: {', '.join(failed_banks)}")
    
    logger.info(f"Successfully aggregated {len(all_rates)} rates from {len(scrapers) - len(failed_banks)} banks")
    return all_rates, failed_banks

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "FX Rate API is running",
        "supported_banks": ["VCB", "Agribank", "Vietinbank", "Techcombank", "TPBank"],
        "supported_currencies": ["USD", "EUR", "JPY", "CNY"],
        "endpoints": {
            "/": "Health check",
            "/api/rates": "Get all exchange rates",
            "/api/rates/<currency>": "Get rates for specific currency",
            "/api/banks": "Get list of supported banks",
            "/api/currencies": "Get list of supported currencies"
        }
    })

@app.route('/api/banks')
def get_banks():
    """Get list of supported banks"""
    return jsonify({
        "status": "success",
        "banks": ["VCB", "Agribank", "Vietinbank", "Techcombank", "TPBank"]
    })

@app.route('/api/currencies')
def get_currencies():
    """Get list of supported currencies"""
    return jsonify({
        "status": "success",
        "currencies": ["USD", "EUR", "JPY", "CNY"]
    })

@app.route('/api/rates')
def get_rates():
    """Get all exchange rates"""
    try:
        rates, failed_banks = aggregate_rates()
        
        if not rates:
            return jsonify({
                "error": "No rates available",
                "failed_banks": failed_banks,
                "data": []
            }), 503
            
        return jsonify({
            "status": "success",
            "data": rates,
            "count": len(rates),
            "failed_banks": failed_banks,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/rates/<currency>')
def get_currency_rates(currency):
    """Get rates for a specific currency"""
    try:
        currency = currency.upper()
        supported_currencies = ["USD", "EUR", "JPY", "CNY"]
        
        if currency not in supported_currencies:
            return jsonify({
                "error": f"Currency {currency} not supported",
                "supported_currencies": supported_currencies
            }), 400
        
        all_rates, failed_banks = aggregate_rates()
        currency_rates = [rate for rate in all_rates if rate['currency'] == currency]
        
        if not currency_rates:
            return jsonify({
                "error": f"No rates found for currency {currency}",
                "failed_banks": failed_banks,
                "data": []
            }), 404
            
        # Add comparison data
        if len(currency_rates) > 1:
            buy_rates = [rate['buy'] for rate in currency_rates]
            sell_rates = [rate['sell'] for rate in currency_rates]
            
            comparison = {
                "best_buy": max(buy_rates),
                "worst_buy": min(buy_rates),
                "best_sell": min(sell_rates),
                "worst_sell": max(sell_rates),
                "buy_spread": max(buy_rates) - min(buy_rates),
                "sell_spread": max(sell_rates) - min(sell_rates)
            }
        else:
            comparison = None
            
        return jsonify({
            "status": "success",
            "currency": currency,
            "data": currency_rates,
            "count": len(currency_rates),
            "failed_banks": failed_banks,
            "comparison": comparison,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_currency_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/rates/<currency>/best')
def get_best_rates(currency):
    """Get best rates for a specific currency"""
    try:
        currency = currency.upper()
        supported_currencies = ["USD", "EUR", "JPY", "CNY"]
        
        if currency not in supported_currencies:
            return jsonify({
                "error": f"Currency {currency} not supported",
                "supported_currencies": supported_currencies
            }), 400
        
        all_rates, failed_banks = aggregate_rates()
        currency_rates = [rate for rate in all_rates if rate['currency'] == currency]
        
        if not currency_rates:
            return jsonify({
                "error": f"No rates found for currency {currency}",
                "failed_banks": failed_banks
            }), 404
        
        # Find best rates
        best_buy = max(currency_rates, key=lambda x: x['buy'])
        best_sell = min(currency_rates, key=lambda x: x['sell'])
        
        return jsonify({
            "status": "success",
            "currency": currency,
            "best_buy": best_buy,
            "best_sell": best_sell,
            "failed_banks": failed_banks,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_best_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.errorhandler()
