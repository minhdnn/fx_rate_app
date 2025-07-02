from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper.vcb import get_vcb_rates
from scraper.agribank import get_agribank_rates
from scraper.vietinbank import get_vietinbank_rates
from scraper.techcombank import get_techcombank_rates
from scraper.tpbank import get_tpbank_rates
import logging
import time
from threading import Lock
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache
_cache = {}
_cache_lock = Lock()
CACHE_DURATION = 300  # 5 minutes in seconds

def get_cached_rates():
    """Get rates from cache if available and not expired"""
    with _cache_lock:
        if 'data' in _cache and 'timestamp' in _cache:
            cache_age = time.time() - _cache['timestamp']
            if cache_age < CACHE_DURATION:
                logger.info(f"Returning cached rates (age: {cache_age:.1f}s)")
                return _cache['data']
    return None

def set_cached_rates(rates):
    """Store rates in cache"""
    with _cache_lock:
        _cache['data'] = rates
        _cache['timestamp'] = time.time()

def aggregate_rates():
    """Aggregate rates from all banks"""
    
    # Try cache first
    cached_rates = get_cached_rates()
    if cached_rates:
        return cached_rates
    
    logger.info("Fetching fresh rates from all banks...")
    
    scrapers = [
        ('VCB', get_vcb_rates),
        ('Agribank', get_agribank_rates),
        ('Vietinbank', get_vietinbank_rates),
        ('Techcombank', get_techcombank_rates),
        ('TP Bank', get_tpbank_rates)
    ]
    
    all_rates = []
    failed_banks = []
    
    for bank_name, scraper_func in scrapers:
        try:
            logger.info(f"Fetching rates from {bank_name}...")
            bank_rates = scraper_func()
            all_rates.extend(bank_rates)
            logger.info(f"Successfully fetched {len(bank_rates)} rates from {bank_name}")
        except Exception as e:
            logger.error(f"Error fetching rates from {bank_name}: {str(e)}")
            failed_banks.append(bank_name)
    
    if failed_banks:
        logger.warning(f"Failed to fetch rates from: {', '.join(failed_banks)}")
    
    logger.info(f"Total rates fetched: {len(all_rates)}")
    
    # Cache the results
    set_cached_rates(all_rates)
    
    return all_rates

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "FX Rate API is running",
        "version": "2.0",
        "supported_banks": ["VCB", "Agribank", "Vietinbank", "Techcombank", "TP Bank"],
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
        "banks": ["VCB", "Agribank", "Vietinbank", "Techcombank", "TP Bank"]
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
        rates = aggregate_rates()
        
        if not rates:
            return jsonify({
                "error": "No rates available",
                "message": "All bank scrapers failed to fetch data",
                "data": []
            }), 503
        
        # Add statistics
        banks = list(set(rate['bank'] for rate in rates))
        currencies = list(set(rate['currency'] for rate in rates))
        
        return jsonify({
            "status": "success",
            "data": rates,
            "count": len(rates),
            "banks": banks,
            "currencies": currencies,
            "timestamp": datetime.now().isoformat(),
            "cache_info": {
                "cached": get_cached_rates() is not None,
                "cache_duration": CACHE_DURATION
            }
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
        
        # Validate currency
        supported_currencies = ["USD", "EUR", "JPY", "CNY"]
        if currency not in supported_currencies:
            return jsonify({
                "error": f"Unsupported currency: {currency}",
                "supported_currencies": supported_currencies
            }), 400
        
        all_rates = aggregate_rates()
        currency_rates = [rate for rate in all_rates if rate['currency'] == currency]
        
        if not currency_rates:
            return jsonify({
                "error": f"No rates found for currency {currency}",
                "message": "This currency might not be available from any banks at the moment",
                "data": []
            }), 404
        
        # Calculate best rates
        best_buy = max(currency_rates, key=lambda x: x['buy'])
        best_sell = min(currency_rates, key=lambda x: x['sell'])
        
        return jsonify({
            "status": "success",
            "currency": currency,
            "data": currency_rates,
            "count": len(currency_rates),
            "best_rates": {
                "best_buy": {
                    "bank": best_buy['bank'],
                    "rate": best_buy['buy']
                },
                "best_sell": {
                    "bank": best_sell['bank'],
                    "rate": best_sell['sell']
                }
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_currency_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/compare/<currency>')
def compare_currency_rates(currency):
    """Compare rates for a specific currency across all banks"""
    try:
        currency = currency.upper()
        
        # Validate currency
        supported_currencies = ["USD", "EUR", "JPY", "CNY"]
        if currency not in supported_currencies:
            return jsonify({
                "error": f"Unsupported currency: {currency}",
                "supported_currencies": supported_currencies
            }), 400
        
        all_rates = aggregate_rates()
        currency_rates = [rate for rate in all_rates if rate['currency'] == currency]
        
        if not currency_rates:
            return jsonify({
                "error": f"No rates found for currency {currency}",
                "data": []
            }), 404
        
        # Sort by best buy rate (highest) and best sell rate (lowest)
        buy_rates = sorted(currency_rates, key=lambda x: x['buy'], reverse=True)
        sell_rates = sorted(currency_rates, key=lambda x: x['sell'])
        
        return jsonify({
            "status": "success",
            "currency": currency,
            "comparison": {
                "best_buy_rates": buy_rates,
                "best_sell_rates": sell_rates
            },
            "count": len(currency_rates),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in compare_currency_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Detailed health check"""
    try:
        # Test each scraper
        scrapers = [
            ('VCB', get_vcb_rates),
            ('Agribank', get_agribank_rates),
            ('Vietinbank', get_vietinbank_rates),
            ('Techcombank', get_techcombank_rates),
            ('TP Bank', get_tpbank_rates)
        ]
        
        status = {}
        for bank_name, scraper_func in scrapers:
            try:
                rates = scraper_func()
                status[bank_name] = {
                    "status": "ok",
                    "rates_count": len(rates)
                }
            except Exception as e:
                status[bank_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Overall health
        working_scrapers = sum(1 for s in status.values() if s["status"] == "ok")
        total_scrapers = len(status)
        health_percentage = (working_scrapers / total_scrapers) * 100
        
        return jsonify({
            "status": "ok" if health_percentage >= 60 else "degraded",
            "health_percentage": health_percentage,
            "scrapers": status,
            "cache_info": {
                "has_cached_data": get_cached_rates() is not None,
                "cache_duration": CACHE_DURATION
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation at the root endpoint"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end"
    }), 500

@app.errorhandler(429)
def rate_limit_error(error):
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Please try again later"
    }), 429

if __name__ == '__main__':
    port = int(__import__('os').environ.get('PORT', 5000))
    debug_mode = __import__('os').environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
