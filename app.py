from flask import Flask, jsonify
from flask_cors import CORS
from scraper.vcb import get_vcb_rates
from scraper.agribank import get_agribank_rates
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_rates():
    """Aggregate rates from all banks"""
    try:
        all_rates = get_vcb_rates() + get_agribank_rates()
        logger.info(f"Successfully fetched {len(all_rates)} rates")
        return all_rates
    except Exception as e:
        logger.error(f"Error aggregating rates: {str(e)}")
        return []

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "FX Rate API is running",
        "endpoints": {
            "/": "Health check",
            "/api/rates": "Get all exchange rates",
            "/api/rates/<currency>": "Get rates for specific currency"
        }
    })

@app.route('/api/rates')
def get_rates():
    """Get all exchange rates"""
    try:
        rates = aggregate_rates()
        
        if not rates:
            return jsonify({
                "error": "No rates available",
                "data": []
            }), 503
            
        return jsonify({
            "status": "success",
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
