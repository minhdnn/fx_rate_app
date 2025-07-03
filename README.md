# FX Rate API 🏦💱

Real-time Vietnamese bank exchange rate aggregator. Compare USD, EUR, JPY, and CNY rates from VCB and Agribank via REST API or CLI.

## 🚀 Quick Start

```bash
git clone https://github.com/yourusername/fx-rate-api.git
cd fx-rate-api
pip install -r requirements.txt

# CLI interface
python main.py

# API server
python app.py
```

## 📊 API Endpoints

**GET** `/api/rates` - All exchange rates  
**GET** `/api/rates/{currency}` - Specific currency (USD, EUR, JPY, CNY)

```json
{
  "status": "success",
  "data": [
    {
      "bank": "VCB",
      "currency": "USD",
      "buy": 24100.0,
      "sell": 24500.0
    }
  ]
}
```

## 🎨 CLI Features

Colorful terminal output with rate comparison:
-  ⭐ Yellow star - Best buy/sell rates
- 

```
Currency: USD
| Bank     | Buy       | Sell      |
|----------|-----------|-----------|
| VCB      | 24100.00  | 24500.00  |
| Agribank | 24120.00⭐| 24480.00⭐|
```

## 🏦 Banks

- **VCB (Vietcombank)** - XML API
- **Agribank** - Web scraping

## 🚀 Deployment

**Render.com** - One-click deployment using `render.yaml`

**Manual:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📁 Structure

```
fx-rate-api/
├── app.py           # Flask API
├── main.py          # CLI interface
├── requirements.txt
├── render.yaml
└── scraper/
    ├── vcb.py
    └── agribank.py
```

## 🛠️ Development

Add new banks:
```python
def get_bank_rates():
    return [{
        'bank': 'Bank Name',
        'currency': 'USD',
        'buy': 24100.0,
        'sell': 24500.0
    }]
```

---

