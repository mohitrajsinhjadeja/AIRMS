"""
🧪 AIRMS Comprehensive Testing Suite
Universal AI Risk & Misinformation API Testing

Following the blueprint testing strategy:
- Unit Tests → Integration Tests → API Tests → E2E Tests → Performance Tests
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import AIRMS modules
from app.main import app
from app.services.risk.enhanced_pipeline import RiskAnalysisPipeline
from app.detectors.pii.detector import PIIDetector
from app.detectors.misinformation.detector import MisinformationDetector
from app.detectors.bias.detector import BiasDetector
from app.api.middleware.rate_limiter import rate_limit_middleware

# Test data following blueprint recommendations
TEST_DATA = {
    "fake_news_examples": [
        "BREAKING: Scientists discover that drinking bleach cures all diseases! Share this before it gets censored!",
        "URGENT: The government is putting mind control chips in vaccines! Wake up sheeple!",
        "EXCLUSIVE: Aliens have landed and are working with the deep state to control humanity!"
    ],
    "real_news_examples": [
        "The Federal Reserve announced a 0.25% interest rate increase following their monthly meeting.",
        "Researchers at Stanford University published a study on renewable energy efficiency in peer-reviewed journal Nature.",
        "The World Health Organization released updated guidelines for pandemic preparedness."
    ],
    "pii_examples": [
        "My SSN is 123-45-6789 and my credit card is 4532-1234-5678-9012",
        "Contact me at john.doe@email.com or call (555) 123-4567",
        "My address is 123 Main St, Anytown, NY 12345"
    ],
    "safe_examples": [
        "The weather is nice today and I'm enjoying a cup of coffee.",
        "I love reading books about science and technology.",
        "The sunset looks beautiful from my window."
    ],
    "bias_examples": [
        "All people from that country are lazy and untrustworthy.",
        "Women are naturally bad at math and science.",
        "Young people today have no work ethic whatsoever."
    ],
    "hallucination_examples": [
        "The Eiffel Tower was built in 1889 by Napoleon Bonaparte using alien technology.",
        "Shakespeare wrote his plays using a quantum computer in the 16th century.",
        "The Great Wall of China is visible from Mars with the naked eye."
    ]
}

class TestUniversalAPI:
    """Test the Universal AI Risk & Misinformation API according to blueprint"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Async HTTP client for testing"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    # ========================================
    # 1️⃣ UNIT TESTING
    # ========================================
    
    def test_pii_detection_module(self):
        """Unit test: PII detection correctly flags sensitive data"""
        detector = PIIDetector()
        
        for pii_text in TEST_DATA["pii_examples"]:
            result = detector.detect_pii(pii_text)
            assert result["has_pii"] == True
            assert result["confidence"] > 0.8
            assert len(result["detected_entities"]) > 0
        
        for safe_text in TEST_DATA["safe_examples"]:
            result = detector.detect_pii(safe_text)
            assert result["has_pii"] == False or result["confidence"] < 0.3

    def test_misinformation_detection_accuracy(self):
        """Unit test: Misinformation detection on known fake vs real content"""
        detector = MisinformationDetector()
        
        # Test fake news detection
        for fake_news in TEST_DATA["fake_news_examples"]:
            result = detector.analyze_misinformation(fake_news)
            assert result["is_misinformation"] == True
            assert result["confidence"] > 0.6
        
        # Test real news (should not be flagged)
        for real_news in TEST_DATA["real_news_examples"]:
            result = detector.analyze_misinformation(real_news)
            assert result["is_misinformation"] == False or result["confidence"] < 0.4

    def test_risk_scoring_calculation(self):
        """Unit test: Risk scoring engine calculates severity correctly"""
        pipeline = RiskAnalysisPipeline()
        
        # High-risk content should get high scores
        high_risk_input = TEST_DATA["fake_news_examples"][0] + " " + TEST_DATA["pii_examples"][0]
        result = asyncio.run(pipeline.analyze_risk(high_risk_input))
        
        assert result["overall_risk_score"] > 70
        assert result["severity_level"] in ["HIGH", "CRITICAL"]
        
        # Safe content should get low scores
        safe_input = TEST_DATA["safe_examples"][0]
        result = asyncio.run(pipeline.analyze_risk(safe_input))
        
        assert result["overall_risk_score"] < 30
        assert result["severity_level"] in ["LOW", "MINIMAL"]

    # ========================================
    # 2️⃣ INTEGRATION TESTING
    # ========================================
    
    @pytest.mark.asyncio
    async def test_risk_pipeline_integration(self):
        """Integration test: Risk analysis pipeline integrates all modules correctly"""
        pipeline = RiskAnalysisPipeline()
        
        test_input = "URGENT: Your SSN 123-45-6789 has been compromised by aliens working with the government!"
        result = await pipeline.analyze_risk(test_input)
        
        # Verify all risk categories are analyzed
        assert "pii_analysis" in result
        assert "misinformation_analysis" in result
        assert "bias_analysis" in result
        assert "overall_risk_score" in result
        
        # Verify high-risk detection
        assert result["pii_analysis"]["has_pii"] == True
        assert result["misinformation_analysis"]["is_misinformation"] == True
        assert result["overall_risk_score"] > 80

    @pytest.mark.asyncio
    async def test_caching_integration(self, async_client):
        """Integration test: Redis cache reduces repeated computation"""
        test_payload = {
            "input": "Test content for caching",
            "context": {"source": "test"},
            "config": {"detectors": ["pii", "misinformation"]}
        }
        
        # First request (should compute)
        start_time = time.time()
        response1 = await async_client.post("/api/v1/risk/analyze", json=test_payload)
        first_duration = time.time() - start_time
        
        # Second request (should use cache)
        start_time = time.time()
        response2 = await async_client.post("/api/v1/risk/analyze", json=test_payload)
        second_duration = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()
        # Cache should make second request faster
        assert second_duration < first_duration * 0.8

    # ========================================
    # 3️⃣ API TESTING
    # ========================================
    
    def test_api_json_structure_validation(self, client):
        """API test: Validate request/response JSON structure"""
        payload = {
            "input": "Test content",
            "context": {"source": "test"},
            "config": {"detectors": ["pii", "misinformation", "bias"]}
        }
        
        response = client.post("/api/v1/risk/analyze", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify required fields according to blueprint
        assert "risk_score" in data
        assert "detected_bias" in data
        assert "hallucination_probability" in data
        assert "PII_leaks" in data
        assert "misinformation_flag" in data
        assert "confidence_metrics" in data
        
        # Verify data types
        assert isinstance(data["risk_score"], (int, float))
        assert isinstance(data["misinformation_flag"], bool)
        assert isinstance(data["confidence_metrics"], dict)

    def test_authentication_jwt_tokens(self, client):
        """API test: JWT authentication works correctly"""
        # Test without token
        response = client.get("/api/v1/analytics/statistics")
        assert response.status_code == 401
        
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/analytics/statistics", headers=headers)
        assert response.status_code == 401

    def test_rate_limiting_protection(self, client):
        """API test: Rate limiting prevents abuse"""
        payload = {"input": "Test", "context": {"source": "test"}}
        
        # Make multiple rapid requests
        responses = []
        for i in range(15):  # Exceed typical rate limit
            response = client.post("/api/v1/risk/analyze", json=payload)
            responses.append(response.status_code)
        
        # Should eventually get rate limited
        assert 429 in responses  # Too Many Requests

    # ========================================
    # 4️⃣ END-TO-END TESTING
    # ========================================
    
    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self, async_client):
        """E2E test: Complete workflow from input → AI analysis → risk scoring → response"""
        
        # Simulate real-world usage
        test_cases = [
            {
                "input": TEST_DATA["fake_news_examples"][0],
                "expected_risk": "HIGH",
                "expected_misinformation": True
            },
            {
                "input": TEST_DATA["pii_examples"][0],
                "expected_risk": "HIGH", 
                "expected_pii": True
            },
            {
                "input": TEST_DATA["safe_examples"][0],
                "expected_risk": "LOW",
                "expected_misinformation": False
            }
        ]
        
        for case in test_cases:
            payload = {
                "input": case["input"],
                "context": {"source": "e2e_test"},
                "config": {"detectors": ["pii", "misinformation", "bias"]}
            }
            
            response = await async_client.post("/api/v1/risk/analyze", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            
            # Verify expected outcomes
            if "expected_misinformation" in case:
                assert data["misinformation_flag"] == case["expected_misinformation"]
            
            if "expected_pii" in case:
                assert data["PII_leaks"] == case["expected_pii"]
            
            # Verify risk level matches expectation
            risk_score = data["risk_score"]
            if case["expected_risk"] == "HIGH":
                assert risk_score > 70
            elif case["expected_risk"] == "LOW":
                assert risk_score < 30

    # ========================================
    # 5️⃣ PERFORMANCE TESTING
    # ========================================
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, async_client):
        """Performance test: Handle multiple concurrent requests"""
        
        async def make_request():
            payload = {
                "input": "Performance test content",
                "context": {"source": "perf_test"}
            }
            response = await async_client.post("/api/v1/risk/analyze", json=payload)
            return response.status_code, time.time()
        
        # Simulate 50 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verify all requests succeeded
        success_count = sum(1 for status, _ in results if status == 200)
        assert success_count >= 45  # Allow for some rate limiting
        
        # Verify reasonable performance (should handle 50 requests in under 30 seconds)
        assert total_time < 30
        
        print(f"✅ Handled {success_count}/50 concurrent requests in {total_time:.2f}s")

    def test_ai_inference_latency(self, client):
        """Performance test: Measure AI inference response times"""
        payload = {
            "input": "This is a test to measure AI inference latency for risk detection.",
            "context": {"source": "latency_test"}
        }
        
        response_times = []
        for _ in range(10):
            start_time = time.time()
            response = client.post("/api/v1/risk/analyze", json=payload)
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        
        # Should respond within reasonable time (adjust based on your requirements)
        assert avg_response_time < 2.0  # 2 seconds max
        
        print(f"✅ Average response time: {avg_response_time:.3f}s")

    # ========================================
    # 6️⃣ SECURITY TESTING
    # ========================================
    
    def test_pii_leakage_prevention(self, client):
        """Security test: Ensure PII doesn't leak in responses"""
        pii_input = "My SSN is 123-45-6789 and credit card is 4532-1234-5678-9012"
        
        payload = {
            "input": pii_input,
            "context": {"source": "security_test"}
        }
        
        response = client.post("/api/v1/risk/analyze", json=payload)
        assert response.status_code == 200
        
        response_text = response.text
        
        # Verify PII is not present in response
        assert "123-45-6789" not in response_text
        assert "4532-1234-5678-9012" not in response_text
        
        # But PII should be detected
        data = response.json()
        assert data["PII_leaks"] == True

    def test_sql_injection_protection(self, client):
        """Security test: API protects against injection attempts"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd"
        ]
        
        for malicious_input in malicious_inputs:
            payload = {
                "input": malicious_input,
                "context": {"source": "security_test"}
            }
            
            response = client.post("/api/v1/risk/analyze", json=payload)
            
            # Should not crash and should sanitize input
            assert response.status_code in [200, 400]  # Either processed safely or rejected
            
            if response.status_code == 200:
                # Verify malicious content is flagged as high risk
                data = response.json()
                assert data["risk_score"] > 50

# ========================================
# 7️⃣ SPECIALIZED TESTS
# ========================================

class TestMultiLanguageSupport:
    """Test multi-language risk detection capabilities"""
    
    def test_language_detection_and_analysis(self, client):
        """Test risk detection works across languages"""
        multilingual_tests = [
            {"text": "Esto es una noticia falsa muy peligrosa", "lang": "es"},
            {"text": "Ceci est une fausse nouvelle dangereuse", "lang": "fr"},
            {"text": "これは危険な偽のニュースです", "lang": "ja"}
        ]
        
        for test_case in multilingual_tests:
            payload = {
                "input": test_case["text"],
                "context": {"source": "multilang_test", "language": test_case["lang"]}
            }
            
            response = client.post("/api/v1/risk/analyze", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            # Should detect risk regardless of language
            assert "risk_score" in data
            assert data["risk_score"] >= 0

class TestAdaptiveGuardrails:
    """Test adaptive learning capabilities"""
    
    @pytest.mark.asyncio
    async def test_threshold_adaptation(self, async_client):
        """Test that system can adapt detection thresholds"""
        # This would test the adaptive guardrails feature
        # Implementation depends on your learning algorithm
        pass

# ========================================
# 8️⃣ FIXTURES AND UTILITIES
# ========================================

@pytest.fixture(scope="session")
def test_database():
    """Setup test database for integration tests"""
    # Setup test MongoDB instance
    pass

@pytest.fixture
def mock_ai_models():
    """Mock AI models for faster testing"""
    with patch('app.services.ai.gemini_service') as mock_gemini, \
         patch('app.services.ai.groq_service') as mock_groq:
        
        # Configure mocks to return predictable results
        mock_gemini.analyze.return_value = {"confidence": 0.8, "result": "test"}
        mock_groq.analyze.return_value = {"confidence": 0.7, "result": "test"}
        
        yield {"gemini": mock_gemini, "groq": mock_groq}

# ========================================
# 9️⃣ BENCHMARK TESTS
# ========================================

class TestBenchmarks:
    """Benchmark tests for performance optimization"""
    
    def test_throughput_benchmark(self, client):
        """Measure API throughput (requests per second)"""
        payload = {"input": "Benchmark test", "context": {"source": "benchmark"}}
        
        start_time = time.time()
        request_count = 100
        
        for _ in range(request_count):
            response = client.post("/api/v1/risk/analyze", json=payload)
            assert response.status_code == 200
        
        total_time = time.time() - start_time
        throughput = request_count / total_time
        
        print(f"✅ Throughput: {throughput:.2f} requests/second")
        
        # Should handle at least 10 requests per second
        assert throughput > 10

if __name__ == "__main__":
    # Run specific test suites
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ])
