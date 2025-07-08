from flask import Flask, jsonify, request
from flask_cors import CORS
from scraper.vcb import get_vcb_rates
from scraper.agribank import get_agribank_rates
from scraper.doji_gold import get_doji_gold_rates, get_gold_charts
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_rates():
    """Aggregate currency rates from all banks"""
    try:
        all_rates = get_vcb_rates() + get_agribank_rates()
        logger.info(f"Successfully fetched {len(all_rates)} currency rates")
        return all_rates
    except Exception as e:
        logger.error(f"Error aggregating currency rates: {str(e)}")
        return []

def aggregate_gold_rates():
    """Aggregate gold rates from DOJI"""
    try:
        gold_rates = get_doji_gold_rates()
        logger.info(f"Successfully fetched {len(gold_rates)} gold rates")
        return gold_rates
    except Exception as e:
        logger.error(f"Error aggregating gold rates: {str(e)}")
        return []

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "FX Rate & Gold Price API is running",
        "endpoints": {
            "/": "Health check",
            "/api/rates": "Get all currency exchange rates",
            "/api/rates/<currency>": "Get rates for specific currency (USD, EUR, JPY, CNY)",
            "/api/gold": "Get all gold prices",
            "/api/gold/<category>": "Get gold prices by category (domestic, international, jewelry)",
            "/api/gold/charts": "Get gold price chart URLs",
            "/api/all": "Get both currency and gold data"
        }
    })

@app.route('/api/rates')
def get_rates():
    """Get all currency exchange rates"""
    try:
        rates = aggregate_rates()
        
        if not rates:
            return jsonify({
                "error": "No currency rates available",
                "data": []
            }), 503
            
        return jsonify({
            "status": "success",
            "type": "currency",
            "data": rates,
            "count": len(rates),
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
        all_rates = aggregate_rates()
        
        currency_rates = [rate for rate in all_rates if rate['currency'] == currency]
        
        if not currency_rates:
            return jsonify({
                "error": f"No rates found for currency {currency}",
                "data": []
            }), 404
            
        return jsonify({
            "status": "success",
            "type": "currency",
            "currency": currency,
            "data": currency_rates,
            "count": len(currency_rates)
        })
    except Exception as e:
        logger.error(f"Error in get_currency_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/gold')
def get_gold_rates():
    """Get all gold prices"""
    try:
        rates = aggregate_gold_rates()
        
        if not rates:
            return jsonify({
                "error": "No gold rates available",
                "data": []
            }), 503
            
        # Group by category for better organization
        categorized_data = {}
        for rate in rates:
            category = rate['category']
            if category not in categorized_data:
                categorized_data[category] = []
            categorized_data[category].append(rate)
            
        return jsonify({
            "status": "success",
            "type": "gold",
            "data": rates,
            "categorized": categorized_data,
            "count": len(rates),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_gold_rates: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/gold/<category>')
def get_gold_by_category(category):
    """Get gold prices by category (domestic, international, jewelry)"""
    try:
        valid_categories = ['domestic', 'international', 'jewelry', 'gold_jewelry']
        if category not in valid_categories:
            return jsonify({
                "error": f"Invalid category. Valid categories: {', '.join(valid_categories)}",
                "data": []
            }), 400
            
        all_rates = aggregate_gold_rates()
        
        # Handle 'jewelry' as alias for 'gold_jewelry'
        search_category = 'gold_jewelry' if category == 'jewelry' else category
        
        filtered_rates = [rate for rate in all_rates if rate['category'] == search_category]
        
        if not filtered_rates:
            return jsonify({
                "error": f"No gold rates found for category {category}",
                "data": []
            }), 404
            
        return jsonify({
            "status": "success",
            "type": "gold",
            "category": category,
            "data": filtered_rates,
            "count": len(filtered_rates)
        })
    except Exception as e:
        logger.error(f"Error in get_gold_by_category: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/gold/charts')
def get_gold_charts_endpoint():
    """Get gold price chart URLs"""
    try:
        charts = get_gold_charts()
        
        if not charts:
            return jsonify({
                "error": "No gold charts available",
                "data": []
            }), 503
            
        return jsonify({
            "status": "success",
            "type": "gold_charts",
            "data": charts,
            "count": len(charts),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_gold_charts: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/all')
def get_all_data():
    """Get both currency and gold data"""
    try:
        currency_rates = aggregate_rates()
        gold_rates = aggregate_gold_rates()
        
        return jsonify({
            "status": "success",
            "data": {
                "currency": {
                    "rates": currency_rates,
                    "count": len(currency_rates)
                },
                "gold": {
                    "rates": gold_rates,
                    "count": len(gold_rates),
                    "categories": {
                        "domestic": [r for r in gold_rates if r['category'] == 'domestic'],
                        "international": [r for r in gold_rates if r['category'] == 'international'],
                        "jewelry": [r for r in gold_rates if r['category'] == 'gold_jewelry']
                    }
                }
            },
            "total_count": len(currency_rates) + len(gold_rates),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_all_data: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on our end"
    }), 500

if __name__ == '__main__':
    port = int(__import__('os').environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
