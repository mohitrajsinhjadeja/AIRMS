"""
🚀 Real-Time Chat API Example Usage
Demonstrates the exact format returned by the new /chat/realtime endpoint
"""

import asyncio
import json
from datetime import datetime

# Example API response format for different risk scenarios
EXAMPLE_RESPONSES = {
    "high_risk_pii": {
        "message": "🚫 **Critical Security Alert** (Risk: 65%)\n\nI've detected critical security concerns in your message related to **PII Detected**. As AIRMS, I cannot process requests with such high risk levels for your safety and security.\n\n**Immediate Actions Required:**\n• Remove personal information from message\n• Use anonymized examples instead\n• Check privacy settings\n\n**Risk Level:** HIGH (65%)\n**Detected Issues:** PII Detected\n**Conversation ID:** 48c9e5f5...",
        "risk_score": 65,
        "risk_flags": ["PII Detected"],
        "conversation_id": "48c9e5f5-7a2b-4c8d-9e1f-2a3b4c5d6e7f",
        "timestamp": "2025-09-26T15:30:00.000Z"
    },
    "medium_risk_bias": {
        "message": "🔍 **Safety Check** (Risk: 35%)\n\nHello! I'm AIRMS (AI Risk Management Assistant). I've noted some considerations regarding **Bias** in your message, but I'm here to help.\n\n**Quick Tip:** Rephrase using inclusive language\n\nWhat specific information can I help you with today?",
        "risk_score": 35,
        "risk_flags": ["Bias"],
        "conversation_id": "a1b2c3d4-e5f6-7890-1234-56789abcdef0",
        "timestamp": "2025-09-26T15:31:00.000Z"
    },
    "safe_interaction": {
        "message": "Hello! I'm AIRMS (AI Risk Management Assistant), and I'm here to help you with AI safety, risk management, and general assistance.\n\nYour message is clear and safe. What can I help you with today?",
        "risk_score": 0,
        "risk_flags": ["None"],
        "conversation_id": "def12345-6789-abcd-ef01-23456789abcd",
        "timestamp": "2025-09-26T15:32:00.000Z"
    },
    "multi_risk_critical": {
        "message": "🚫 **Critical Security Alert** (Risk: 85%)\n\nI've detected critical security concerns in your message related to **PII Detected, Adversarial Intent**. As AIRMS, I cannot process requests with such high risk levels for your safety and security.\n\n**Immediate Actions Required:**\n• Remove personal information from message\n• Rephrase request without manipulation attempts\n• Use direct, clear questions\n\n**Risk Level:** CRITICAL (85%)\n**Detected Issues:** PII Detected, Adversarial Intent\n**Conversation ID:** 12345678...",
        "risk_score": 85,
        "risk_flags": ["PII Detected", "Adversarial Intent"],
        "conversation_id": "12345678-9abc-def0-1234-56789abcdef0",
        "timestamp": "2025-09-26T15:33:00.000Z"
    }
}

def demonstrate_api_responses():
    """Demonstrate the API response format for frontend integration"""
    
    print("🚀 AIRMS Real-Time Chat API - Response Format Examples")
    print("=" * 70)
    print()
    
    for scenario, response in EXAMPLE_RESPONSES.items():
        print(f"📋 Scenario: {scenario.upper().replace('_', ' ')}")
        print("-" * 50)
        
        # Show how frontend would use the data
        risk_display = f"{response['risk_score']}%" if response['risk_score'] > 0 else "Safe"
        flags_display = ", ".join(response['risk_flags']) if response['risk_flags'] != ["None"] else "No Issues"
        
        print(f"Frontend Display:")
        print(f"  💬 Message: {response['message'][:100]}{'...' if len(response['message']) > 100 else ''}")
        print(f"  🎯 Risk Level: {risk_display}")
        print(f"  🚩 Flags: {flags_display}")
        print(f"  🆔 Conversation: {response['conversation_id'][:13]}...")
        print(f"  ⏰ Time: {response['timestamp']}")
        print()
        
        # Show JSON format for API
        print("JSON Response Format:")
        print(json.dumps(response, indent=2))
        print()
        print("=" * 70)
        print()

def show_frontend_integration_example():
    """Show how frontend dashboard would integrate this data"""
    
    print("🖥️  Frontend Dashboard Integration Example")
    print("=" * 50)
    
    example_dashboard_code = '''
// React Component Example
const ChatMessage = ({ chatResponse }) => {
    const { message, risk_score, risk_flags, timestamp } = chatResponse;
    
    // Determine risk level and color
    const getRiskLevel = (score) => {
        if (score === 0) return { level: "Safe", color: "#4CAF50" };
        if (score <= 25) return { level: "Low", color: "#FF9800" };
        if (score <= 50) return { level: "Medium", color: "#FF5722" };
        if (score <= 75) return { level: "High", color: "#F44336" };
        return { level: "Critical", color: "#D32F2F" };
    };
    
    const riskInfo = getRiskLevel(risk_score);
    const flagsDisplay = risk_flags.join(", ");
    
    return (
        <div className="chat-message">
            <div className="message-content">{message}</div>
            <div className="risk-indicator" style={{ color: riskInfo.color }}>
                {riskInfo.level} ({risk_score}%) - {flagsDisplay}
            </div>
            <div className="timestamp">{timestamp}</div>
        </div>
    );
};

// Dashboard Analytics Example
const RiskDashboard = () => {
    const [chatStats, setChatStats] = useState(null);
    
    useEffect(() => {
        fetch('/api/v1/chat/risk-stats')
            .then(res => res.json())
            .then(data => setChatStats(data));
    }, []);
    
    return (
        <div className="dashboard">
            <div className="stat-card">
                <h3>Total Chats: {chatStats?.overview.total_chats}</h3>
                <p>Risk Detections: {chatStats?.overview.total_risk_detections}</p>
                <p>Average Risk: {chatStats?.overview.average_risk_score}%</p>
            </div>
        </div>
    );
};
'''
    
    print(example_dashboard_code)

def show_api_endpoints():
    """Show available API endpoints"""
    
    print("🔗 Available AIRMS Chat API Endpoints")
    print("=" * 50)
    
    endpoints = [
        {
            "endpoint": "POST /api/v1/chat/realtime",
            "description": "Real-time chat with dynamic risk scoring",
            "request_format": {
                "message": "User input message",
                "conversation_id": "optional-conversation-id",
                "context": {"optional": "context"}
            },
            "response_format": {
                "message": "AI response",
                "risk_score": "0-100",
                "risk_flags": ["Array of detected risks"],
                "conversation_id": "unique-id",
                "timestamp": "ISO timestamp"
            }
        },
        {
            "endpoint": "POST /api/v1/chat/completion",
            "description": "Complete chat response with detailed risk analysis",
            "response_format": "Full ChatResponse object with messages, risk_analysis, and session_metadata"
        },
        {
            "endpoint": "GET /api/v1/chat/risk-stats",
            "description": "Real-time risk statistics for dashboard",
            "response_format": "Risk distribution, categories, and analytics data"
        }
    ]
    
    for endpoint_info in endpoints:
        print(f"🔹 {endpoint_info['endpoint']}")
        print(f"   Description: {endpoint_info['description']}")
        if 'request_format' in endpoint_info:
            print(f"   Request: {json.dumps(endpoint_info['request_format'], indent=6)}")
        print(f"   Response: {json.dumps(endpoint_info['response_format'], indent=6) if isinstance(endpoint_info['response_format'], dict) else endpoint_info['response_format']}")
        print()

def main():
    """Run the demonstration"""
    demonstrate_api_responses()
    show_api_endpoints()
    show_frontend_integration_example()
    
    print("🎯 Key Benefits of Enhanced AIRMS System:")
    print("=" * 50)
    print("✅ Deterministic risk scoring (not left entirely to LLM)")
    print("✅ Real-time risk flags: ['PII Detected'], ['Bias'], etc.")
    print("✅ Frontend-ready response format")
    print("✅ MongoDB logging for analytics and compliance")
    print("✅ System prompt integration for consistent behavior")
    print("✅ Input AND output risk analysis (70%/30% weighting)")
    print("✅ Enhanced PII detection (Indian Aadhaar, PAN, etc.)")
    print("✅ Multi-risk penalty system")
    print()
    print("🚀 Your dashboard can now show:")
    print("   • Real-time risk scores: Low Risk (15%) or High Risk (85%)")
    print("   • Dynamic flags: ['PII Detected'] or ['None']")
    print("   • Live analytics and historical trends")
    print("   • Conversation-level risk tracking")

if __name__ == "__main__":
    main()