# FX Rate & Gold Price API 🏦💰

A comprehensive Vietnamese financial data aggregator that provides real-time exchange rates and gold prices through both REST API and CLI interfaces.

## ✨ Features

- **Currency Exchange Rates**: USD, EUR, JPY, CNY from VCB and Agribank
- **Gold Prices**: Domestic, international, and jewelry prices from DOJI
- **Dual Interface**: REST API and colorful CLI
- **Real-time Data**: Live scraping from official sources
- **Easy Deployment**: One-click deployment to Render.com

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/fx-rate-api.git
cd fx-rate-api
pip install -r requirements.txt
```

### CLI Usage

```bash
# Show market summary (default)
python main.py

# Currency exchange rates only
python main.py --currency

# Gold prices only
python main.py --gold

# Gold chart URLs
python main.py --charts

# Show everything
python main.py --all
```

### API Server

```bash
python app.py
# Server runs on http://localhost:5000
```

## 📊 API Endpoints

### Currency Exchange Rates

| Endpoint | Description |
|----------|-------------|
| `GET /api/rates` | All exchange rates |
| `GET /api/rates/{currency}` | Specific currency (USD, EUR, JPY, CNY) |

### Gold Prices

| Endpoint | Description |
|----------|-------------|
| `GET /api/gold` | All gold prices |
| `GET /api/gold/{category}` | Gold by category (domestic, international, jewelry) |
| `GET /api/gold/charts` | Gold chart URLs |

### Combined Data

| Endpoint | Description |
|----------|-------------|
| `GET /api/all` | Both currency and gold data |
| `GET /` | Health check and API documentation |

## 📋 Response Format

### Currency Rates

```json
{
  "status": "success",
  "type": "currency",
  "data": [
    {
      "bank": "VCB",
      "currency": "USD",
      "buy": 24100.0,
      "sell": 24500.0
    },
    {
      "bank": "Agribank",
      "currency": "USD",
      "buy": 24120.0,
      "sell": 24480.0
    }
  ],
  "count": 2,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Gold Prices

```json
{
  "status": "success",
  "type": "gold",
  "data": [
    {
      "type": "gold",
      "category": "domestic",
      "name": "SJC Gold",
      "original_name": "Vàng SJC",
      "buy": 73500000,
      "sell": 75000000,
      "unit": "VND/tael",
      "last_updated": "2024-01-15 10:30:00"
    }
  ],
  "categorized": {
    "domestic": [...],
    "international": [...],
    "jewelry": [...]
  },
  "count": 25,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🎨 CLI Features

The CLI provides colorful, formatted output with:

- **Star indicators (⭐)** for best buy/sell rates
- **Color-coded categories** for easy reading
- **Formatted tables** with proper alignment
- **Summary view** showing market overview
- **Chart URLs** for technical analysis

### CLI Examples

```bash
# Currency rates with best rate highlighting
Currency: USD
| Bank       | Buy       | Sell      |
|------------|-----------|-----------|
| VCB        | 24,100.00 | 24,500.00 |
| Agribank   | 24,120.00⭐| 24,480.00⭐|

# Gold prices by category
🏠 DOMESTIC GOLD PRICES
| Name                     | Buy        | Sell       | Unit      |
|--------------------------|------------|------------|-----------|
| SJC Gold                 | 73,500,000 | 75,000,000 | VND/tael  |
| DOJI Gold                | 73,400,000 | 74,900,000 | VND/tael  |
```

## 🏦 Data Sources

### Banks (Currency Exchange)
- **VCB (Vietcombank)**: XML API from official portal
- **Agribank**: Web scraping from official website

### Gold Prices
- **DOJI**: Official XML API covering:
  - Domestic gold bars and coins
  - International gold (USD/oz)
  - Jewelry prices (various karats)
  - Historical charts

## 🚀 Deployment

### Render.com (Recommended)

1. Fork this repository
2. Connect to Render.com
3. Deploy using the included `render.yaml`
4. Done! Your API is live

### Manual Deployment

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use Python directly
python app.py
```

### Environment Variables

```bash
PORT=5000  # Server port (default: 5000)
```

## 📁 Project Structure

```
fx-rate-api/
├── app.py                 # Flask API server
├── main.py               # CLI interface
├── requirements.txt      # Python dependencies
├── render.yaml          # Render.com deployment config
├── runtime.txt          # Python version
└── scraper/
    ├── vcb.py           # VCB exchange rates
    ├── agribank.py      # Agribank exchange rates
    └── doji_gold.py     # DOJI gold prices
```

## 🛠️ Development

### Adding New Banks

```python
# In scraper/new_bank.py
def get_new_bank_rates():
    # Your scraping logic here
    return [{
        'bank': 'Bank Name',
        'currency': 'USD',
        'buy': 24100.0,
        'sell': 24500.0
    }]

# In app.py
from scraper.new_bank import get_new_bank_rates

def aggregate_rates():
    return get_vcb_rates() + get_agribank_rates() + get_new_bank_rates()
```

### Adding New Gold Sources

```python
# In scraper/new_gold_source.py
def get_new_gold_rates():
    return [{
        'type': 'gold',
        'category': 'domestic',
        'name': 'Gold Name',
        'buy': 73500000,
        'sell': 75000000,
        'unit': 'VND/tael'
    }]
```

## 🔧 Dependencies

- **requests**: HTTP requests
- **beautifulsoup4**: HTML parsing
- **lxml**: XML parsing
- **colorama**: Terminal colors
- **flask**: Web framework
- **flask-cors**: CORS support

## 📊 Usage Examples

### Python Client

```python
import requests

# Get all currency rates
response = requests.get('https://your-api.com/api/rates')
rates = response.json()

# Get USD rates only
response = requests.get('https://your-api.com/api/rates/USD')
usd_rates = response.json()

# Get gold prices
response = requests.get('https://your-api.com/api/gold')
gold_prices = response.json()
```

### JavaScript Client

```javascript
// Fetch currency rates
fetch('/api/rates')
  .then(response => response.json())
  .then(data => console.log(data));

// Fetch gold prices by category
fetch('/api/gold/domestic')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 🔍 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `404`: Currency/category not found
- `500`: Internal server error
- `503`: Service unavailable (data source down)

Error responses include helpful messages:

```json
{
  "error": "No rates found for currency XYZ",
  "data": []
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

