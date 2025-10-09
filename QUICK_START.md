# 🚀 AIRMS Quick Start Guide
## Universal AI Risk & Misinformation API

**Get your AIRMS system running in 5 minutes!**

## 📋 Prerequisites

- **Python 3.8+** 
- **Node.js 18+**
- **MongoDB** (local or cloud)
- **Git**

## ⚡ Quick Deploy (Automated)

### Option 1: One-Command Deployment

```powershell
# Windows PowerShell
.\deploy-complete.ps1 -Platform local

# This will:
# ✅ Setup backend with all dependencies
# ✅ Setup frontend dashboard  
# ✅ Run comprehensive tests
# ✅ Start both servers
# ✅ Validate system health
```

### Option 2: Docker Deployment

```powershell
.\deploy-complete.ps1 -Platform docker
```

## 🔧 Manual Setup (If you prefer step-by-step)

### 1️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download AI models
python -m spacy download en_core_web_sm

# Setup database
python scripts/setup_database.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Test Your Installation

### Quick API Test

```bash
# Test health
curl http://localhost:8000/health

# Test risk analysis
curl -X POST "http://localhost:8000/api/v1/risk/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "My SSN is 123-45-6789. This BREAKING news will shock you!",
    "context": {"source": "test"},
    "config": {"detectors": ["pii", "misinformation"]}
  }'
```

### Run Complete System Test

```bash
python test_complete_system.py
```

## 🔗 Access Points

After successful deployment:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | Main API endpoint |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Frontend Dashboard** | http://localhost:3000 | Web dashboard |
| **Health Check** | http://localhost:8000/health | System status |
| **Real-time Metrics** | http://localhost:8000/api/v1/analytics/real-time-metrics | Performance data |

## 🎯 First API Call

### Python Example

```python
import requests

# Analyze content for risks
response = requests.post('http://localhost:8000/api/v1/risk/analyze', json={
    "input": "Your AI-generated content here",
    "context": {"source": "chatbot"},
    "config": {"detectors": ["pii", "misinformation", "bias"]}
})

result = response.json()
print(f"Risk Score: {result['risk_score']}")
print(f"PII Detected: {result['PII_leaks']}")
print(f"Misinformation: {result['misinformation_flag']}")
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:8000/api/v1/risk/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    input: 'Content to analyze',
    context: {source: 'app'},
    config: {detectors: ['pii', 'misinformation']}
  })
});

const result = await response.json();
console.log('Risk Analysis:', result);
```

## 🔧 Configuration

### Environment Variables

Update `backend/.env` with your settings:

```env
# AI API Keys
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Database
MONGODB_URL=mongodb://localhost:27017/airms

# Security
JWT_SECRET_KEY=your_secret_key_here
```

### Risk Thresholds

Customize detection sensitivity in your API calls:

```json
{
  "config": {
    "thresholds": {
      "risk_threshold": 70,
      "confidence_threshold": 0.8
    },
    "detectors": ["pii", "misinformation", "bias", "hallucination"]
  }
}
```

## 📊 Monitor Performance

### Real-time Metrics

```bash
curl http://localhost:8000/api/v1/analytics/real-time-metrics
```

### Performance Dashboard

Visit http://localhost:3000/dashboard for:
- ✅ Real-time risk analysis charts
- ✅ Performance metrics
- ✅ System health monitoring
- ✅ Request analytics

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check MongoDB connection
python -c "import pymongo; print('MongoDB OK')"
```

**Frontend won't start:**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API returns errors:**
```bash
# Check logs
tail -f backend/logs/app.log

# Test health endpoint
curl http://localhost:8000/health
```

### Get Help

- **Documentation**: See `API_DOCUMENTATION.md`
- **System Test**: Run `python test_complete_system.py`
- **Logs**: Check `backend/logs/` directory
- **Issues**: Check the deployment log file

## 🎉 Next Steps

1. **Configure AI APIs**: Add your Groq/Gemini API keys
2. **Customize Detection**: Adjust risk thresholds for your use case
3. **Integrate**: Use the API in your applications
4. **Monitor**: Set up alerts and monitoring
5. **Scale**: Deploy to production with Docker/Kubernetes

## 🔒 Security Notes

- ✅ All PII is automatically masked in responses
- ✅ Rate limiting prevents abuse
- ✅ JWT authentication for secure access
- ✅ Input sanitization prevents injection attacks
- ✅ Comprehensive audit logging

## 📈 Performance Expectations

- **Response Time**: <200ms for typical requests
- **Throughput**: 100+ requests/second
- **Accuracy**: 90%+ for PII and misinformation detection
- **Uptime**: 99.9% availability target

---

**🎯 Your Universal AI Risk & Misinformation API is now ready!**

Start analyzing AI content for risks, PII leaks, bias, and misinformation with enterprise-grade accuracy and performance.
