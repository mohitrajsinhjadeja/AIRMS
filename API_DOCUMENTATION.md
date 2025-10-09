# 🚀 AIRMS Universal AI Risk & Misinformation API Documentation

## 📋 Overview

The AIRMS API is a **Universal AI Risk & Misinformation Detection System** that can analyze any AI-generated content or model outputs for:

- **Risk Assessment**: PII leaks, bias, hallucinations, adversarial attacks
- **Misinformation Detection**: Fact-checking, source validation, confidence scoring
- **Security Analysis**: Content sanitization, threat detection
- **Compliance**: GDPR/CCPA compliance checking

## 🎯 Core Features

### ✅ **Universal Input Support**
- Any AI-generated text content
- Chatbot responses
- Model outputs
- User-generated content
- Enterprise pipeline data

### ✅ **Structured JSON Output**
```json
{
  "risk_score": 85.5,
  "detected_bias": true,
  "hallucination_probability": 0.73,
  "PII_leaks": true,
  "misinformation_flag": false,
  "confidence_metrics": {
    "overall_confidence": 0.89,
    "pii_confidence": 0.95,
    "bias_confidence": 0.82,
    "misinformation_confidence": 0.76
  },
  "severity_level": "HIGH",
  "detected_entities": [...],
  "mitigation_actions": [...],
  "processing_time_ms": 145
}
```

## 🔗 Base URL

```
Production: https://api.airms.ai
Development: http://localhost:8000
```

## 🔐 Authentication

All API requests require authentication using JWT tokens:

```bash
Authorization: Bearer <your_jwt_token>
```

### Get Access Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## 📊 Core Endpoints

### 1️⃣ **Universal Risk Analysis**

**The main endpoint for analyzing any content:**

```bash
POST /api/v1/risk/analyze
```

**Request Body:**
```json
{
  "input": "Your AI-generated content here",
  "context": {
    "source": "chatbot|app|pipeline|dashboard",
    "user_id": "optional_user_id",
    "session_id": "optional_session_id",
    "language": "en"
  },
  "config": {
    "detectors": ["pii", "misinformation", "bias", "hallucination", "adversarial"],
    "thresholds": {
      "risk_threshold": 70,
      "confidence_threshold": 0.8
    },
    "return_evidence": true,
    "enable_caching": true
  }
}
```

**Response:**
```json
{
  "request_id": "req_123456789",
  "timestamp": "2025-01-08T12:30:45Z",
  "input_hash": "sha256_hash_of_input",
  "analysis_results": {
    "overall_risk_score": 85.5,
    "severity_level": "HIGH",
    "risk_categories": {
      "pii_analysis": {
        "has_pii": true,
        "confidence": 0.95,
        "detected_types": ["ssn", "credit_card", "email"],
        "masked_content": "My SSN is ***-**-**** and email is ****@****.com"
      },
      "misinformation_analysis": {
        "is_misinformation": false,
        "confidence": 0.76,
        "fact_check_sources": ["reuters", "ap_news"],
        "credibility_score": 0.82
      },
      "bias_analysis": {
        "has_bias": true,
        "confidence": 0.82,
        "bias_types": ["gender", "racial"],
        "bias_score": 0.67
      },
      "hallucination_analysis": {
        "is_hallucination": false,
        "confidence": 0.71,
        "factual_accuracy": 0.88
      },
      "adversarial_analysis": {
        "is_adversarial": false,
        "confidence": 0.69,
        "attack_types": []
      }
    }
  },
  "mitigation_actions": [
    {
      "action": "MASK_PII",
      "description": "Sensitive information detected and masked",
      "priority": "HIGH"
    },
    {
      "action": "FLAG_BIAS",
      "description": "Potential bias detected, review recommended",
      "priority": "MEDIUM"
    }
  ],
  "compliance_flags": {
    "gdpr_relevant": true,
    "ccpa_relevant": true,
    "requires_consent": true
  },
  "performance_metrics": {
    "processing_time_ms": 145,
    "cache_hit": false,
    "ai_model_used": "gemini-2.0-flash"
  }
}
```

### 2️⃣ **Batch Analysis**

For analyzing multiple inputs efficiently:

```bash
POST /api/v1/risk/analyze/batch
```

**Request Body:**
```json
{
  "inputs": [
    {
      "id": "input_1",
      "content": "First piece of content to analyze",
      "context": {"source": "chatbot"}
    },
    {
      "id": "input_2", 
      "content": "Second piece of content to analyze",
      "context": {"source": "app"}
    }
  ],
  "config": {
    "detectors": ["pii", "misinformation"],
    "parallel_processing": true
  }
}
```

### 3️⃣ **Real-time Stream Analysis**

For continuous monitoring:

```bash
POST /api/v1/risk/analyze/stream
```

**WebSocket Connection:**
```javascript
const ws = new WebSocket('wss://api.airms.ai/api/v1/risk/stream');

ws.send(JSON.stringify({
  "content": "Real-time content to analyze",
  "context": {"source": "live_chat"}
}));

ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  console.log('Risk analysis:', result);
};
```

### 4️⃣ **Analytics & Monitoring**

```bash
GET /api/v1/analytics/statistics?days=30
GET /api/v1/analytics/risk-timeline?days=7
GET /api/v1/analytics/real-time-metrics
```

## 🔧 Configuration Options

### Risk Detection Thresholds

```json
{
  "thresholds": {
    "low_risk": 30,
    "medium_risk": 60, 
    "high_risk": 80,
    "critical_risk": 90
  }
}
```

### Detector Configuration

```json
{
  "detectors": {
    "pii": {
      "enabled": true,
      "sensitivity": "high",
      "types": ["ssn", "credit_card", "email", "phone", "address"]
    },
    "misinformation": {
      "enabled": true,
      "fact_check_apis": ["google", "snopes", "factcheck_org"],
      "confidence_threshold": 0.7
    },
    "bias": {
      "enabled": true,
      "categories": ["gender", "race", "religion", "political"],
      "sensitivity": "medium"
    }
  }
}
```

## 📈 Rate Limits

| Plan | Requests/Minute | Requests/Hour | Requests/Day |
|------|----------------|---------------|--------------|
| Free | 60 | 1,000 | 10,000 |
| Pro | 300 | 10,000 | 100,000 |
| Enterprise | 1,000 | 50,000 | 1,000,000 |

## 🚀 Quick Start Examples

### Python Example

```python
import requests
import json

# Authentication
auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = auth_response.json()['access_token']

# Risk Analysis
headers = {'Authorization': f'Bearer {token}'}
payload = {
    "input": "My SSN is 123-45-6789. This BREAKING news will shock you!",
    "context": {"source": "chatbot"},
    "config": {"detectors": ["pii", "misinformation"]}
}

response = requests.post(
    'http://localhost:8000/api/v1/risk/analyze',
    headers=headers,
    json=payload
)

result = response.json()
print(f"Risk Score: {result['analysis_results']['overall_risk_score']}")
print(f"PII Detected: {result['analysis_results']['risk_categories']['pii_analysis']['has_pii']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

async function analyzeContent() {
  // Authentication
  const authResponse = await axios.post('http://localhost:8000/api/v1/auth/login', {
    email: 'user@example.com',
    password: 'password'
  });
  
  const token = authResponse.data.access_token;
  
  // Risk Analysis
  const response = await axios.post('http://localhost:8000/api/v1/risk/analyze', {
    input: 'Analyze this AI-generated content for risks',
    context: { source: 'app' },
    config: { detectors: ['pii', 'misinformation', 'bias'] }
  }, {
    headers: { Authorization: `Bearer ${token}` }
  });
  
  console.log('Analysis Result:', response.data);
}

analyzeContent();
```

### cURL Example

```bash
# Get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Analyze content
curl -X POST "http://localhost:8000/api/v1/risk/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Content to analyze for AI risks and misinformation",
    "context": {"source": "api_test"},
    "config": {"detectors": ["pii", "misinformation", "bias"]}
  }'
```

## 🔍 Use Cases

### 1️⃣ **Chatbot Safety**
```python
# Before sending chatbot response to user
response_text = chatbot.generate_response(user_input)
safety_check = airms_api.analyze(response_text)

if safety_check['risk_score'] > 70:
    response_text = "I apologize, but I cannot provide that information."
```

### 2️⃣ **Content Moderation**
```python
# Moderate user-generated content
for post in user_posts:
    analysis = airms_api.analyze(post.content)
    if analysis['misinformation_flag']:
        post.flag_as_misinformation()
    if analysis['PII_leaks']:
        post.mask_sensitive_data()
```

### 3️⃣ **Enterprise Pipeline**
```python
# Integrate into ML pipeline
def process_ai_output(model_output):
    risk_analysis = airms_api.analyze(model_output)
    
    if risk_analysis['severity_level'] in ['HIGH', 'CRITICAL']:
        # Route to human review
        return route_to_human_review(model_output, risk_analysis)
    else:
        return model_output
```

## 🛡️ Security Features

- **PII Masking**: Automatically masks detected sensitive information
- **Input Sanitization**: Prevents injection attacks
- **Rate Limiting**: Protects against abuse
- **Audit Logging**: Complete request/response logging
- **Encryption**: All data encrypted in transit and at rest

## 📊 Monitoring & Analytics

Access comprehensive analytics through the dashboard or API:

- **Risk Score Trends**: Track risk patterns over time
- **Detection Accuracy**: Monitor false positive/negative rates  
- **Performance Metrics**: Response times, throughput, cache hit rates
- **Usage Statistics**: API calls, user activity, resource utilization

## 🚨 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and required fields |
| 401 | Unauthorized | Verify JWT token is valid and not expired |
| 403 | Forbidden | Check API permissions and rate limits |
| 422 | Validation Error | Review input validation requirements |
| 429 | Rate Limited | Reduce request frequency or upgrade plan |
| 500 | Server Error | Contact support if persistent |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {
      "field": "input",
      "issue": "Content exceeds maximum length of 50,000 characters"
    },
    "request_id": "req_123456789",
    "timestamp": "2025-01-08T12:30:45Z"
  }
}
```

## 🔗 SDKs & Libraries

### Official SDKs
- **Python**: `pip install airms-python`
- **JavaScript/Node.js**: `npm install airms-js`
- **Java**: Maven/Gradle dependency available
- **Go**: `go get github.com/airms/airms-go`

### Community Libraries
- **PHP**: airms-php
- **Ruby**: airms-ruby  
- **C#/.NET**: AIRMS.NET

## 📞 Support

- **Documentation**: https://docs.airms.ai
- **API Status**: https://status.airms.ai
- **Support Email**: support@airms.ai
- **GitHub Issues**: https://github.com/airms/airms-api/issues

## 🔄 Changelog

### v1.0.0 (Latest)
- ✅ Universal risk analysis endpoint
- ✅ Multi-language support
- ✅ Real-time streaming analysis
- ✅ Comprehensive PII detection
- ✅ Advanced misinformation detection
- ✅ Batch processing capabilities
- ✅ WebSocket support for real-time monitoring

---

**Ready to secure your AI applications? Start with our [Quick Start Guide](https://docs.airms.ai/quickstart) or explore the [Interactive API Explorer](https://api.airms.ai/docs).**
