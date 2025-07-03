FX Rate API 🏦💱
A real-time foreign exchange rate aggregator for Vietnamese banks. Compare USD, EUR, JPY, and CNY rates across VCB and Agribank through a REST API or colorful CLI.
🚀 Quick Start
bash# Clone and install
git clone https://github.com/yourusername/fx-rate-api.git
cd fx-rate-api
pip install -r requirements.txt

# Run CLI
python main.py

# Start API server
python app.py
API available at http://localhost:5000
📊 API Endpoints
GET /api/rates - All exchange rates
GET /api/rates/{currency} - Specific currency rates (USD, EUR, JPY, CNY)
json{
  "status": "success",
  "data": [
    {
      "bank": "VCB",
      "currency": "USD",
      "buy": 24100.0,
      "sell": 24500.0
    }
  ],
  "count": 8
}
🏦 Supported Banks

VCB (Vietcombank) - XML API integration
Agribank - Web scraping

🎨 CLI Features
Run python main.py to see a beautiful terminal interface:
Currency: USD
| Bank       | Buy       | Sell      |
|------------|-----------|-----------|
| VCB        | 24100.00  | 24500.00  |
| Agribank   | 24120.00⭐| 24480.00⭐|

🟢 Green stars highlight best buy rates
🔴 Red stars highlight best sell rates
Colorful, easy-to-read format

🔧 Configuration
Environment Variables
bashPORT=5000                    # API server port
FLASK_ENV=production         # Flask environment
Supported Currencies

USD - US Dollar
EUR - Euro
JPY - Japanese Yen
CNY - Chinese Yuan

🚀 Deployment
Render.com - One-click deployment using render.yaml
Manual Server:
bashpip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
📁 Project Structure
fx-rate-api/
├── app.py                 # Flask API server
├── main.py               # CLI interface
├── requirements.txt      # Dependencies
├── render.yaml          # Deployment config
└── scraper/
    ├── vcb.py           # Vietcombank scraper
    └── agribank.py      # Agribank scraper
🛠️ Development
Add new banks by creating scrapers in scraper/ directory:
pythondef get_bank_rates():
    return [
        {
            'bank': 'Bank Name',
            'currency': 'USD',
            'buy': 24100.0,
            'sell': 24500.0
        }
    ]
🤝 Contributing

Fork the repository
Create a feature branch
Commit your changes
Push and open a Pull Request
