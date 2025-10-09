#!/usr/bin/env python3
"""
🧪 AIRMS Complete System Integration Test
Universal AI Risk & Misinformation API - End-to-End System Validation

This script validates the entire AIRMS system according to the blueprint:
- Universal API functionality
- All risk detection modules
- Performance benchmarks
- Security features
- Real-world use cases
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestResult:
    def __init__(self, test_name: str, success: bool, response_time_ms: float, 
                 details: Dict[str, Any], error_message: str = ""):
        self.test_name = test_name
        self.success = success
        self.response_time_ms = response_time_ms
        self.details = details
        self.error_message = error_message

class AIRMSSystemTester:
    """Complete system tester for AIRMS Universal API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results: List[TestResult] = []
        
        # Test data following the blueprint
        self.test_data = {
            "high_risk_content": [
                "URGENT: Your SSN 123-45-6789 has been compromised! Click here immediately to secure your account!",
                "BREAKING: Scientists confirm drinking bleach cures COVID! Government doesn't want you to know!",
                "All immigrants are criminals and terrorists who want to destroy our country!",
                "The Earth is flat and NASA is lying to everyone about space travel using CGI!"
            ],
            "medium_risk_content": [
                "I think people from that country tend to be less reliable workers.",
                "This new treatment might cure cancer, though more research is needed.",
                "My email is john.doe@example.com if you need to contact me."
            ],
            "low_risk_content": [
                "The weather is beautiful today and I'm enjoying a nice cup of coffee.",
                "I love reading books about science and technology in my free time.",
                "The new restaurant downtown has excellent reviews and great food."
            ],
            "multilingual_content": [
                {"text": "Esta es una noticia falsa muy peligrosa", "language": "es"},
                {"text": "Ceci est une fausse nouvelle dangereuse", "language": "fr"},
                {"text": "これは危険な偽のニュースです", "language": "ja"}
            ]
        }
    
    async def setup(self):
        """Initialize the test session"""
        self.session = aiohttp.ClientSession()
        logger.info("🔧 Setting up AIRMS system test...")
    
    async def cleanup(self):
        """Clean up test session"""
        if self.session:
            await self.session.close()
        logger.info("🧹 Test cleanup completed")
    
    async def test_system_health(self) -> TestResult:
        """Test 1: System health and availability"""
        logger.info("🏥 Testing system health...")
        
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        test_name="System Health Check",
                        success=True,
                        response_time_ms=response_time,
                        details=data
                    )
                else:
                    return TestResult(
                        test_name="System Health Check",
                        success=False,
                        response_time_ms=response_time,
                        details={},
                        error_message=f"Health check failed with status {response.status}"
                    )
        except Exception as e:
            return TestResult(
                test_name="System Health Check",
                success=False,
                response_time_ms=0,
                details={},
                error_message=str(e)
            )
    
    async def test_api_documentation(self) -> TestResult:
        """Test 2: API documentation accessibility"""
        logger.info("📚 Testing API documentation...")
        
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                response_time = (time.time() - start_time) * 1000
                
                success = response.status == 200
                return TestResult(
                    test_name="API Documentation",
                    success=success,
                    response_time_ms=response_time,
                    details={"status_code": response.status}
                )
        except Exception as e:
            return TestResult(
                test_name="API Documentation",
                success=False,
                response_time_ms=0,
                details={},
                error_message=str(e)
            )
    
    async def test_universal_risk_analysis(self) -> TestResult:
        """Test 3: Universal risk analysis endpoint - Core functionality"""
        logger.info("🎯 Testing universal risk analysis...")
        
        test_payload = {
            "input": self.test_data["high_risk_content"][0],
            "context": {"source": "system_test", "test_id": "universal_api_test"},
            "config": {
                "detectors": ["pii", "misinformation", "bias", "hallucination"],
                "return_evidence": True
            }
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/risk/analyze",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure according to blueprint
                    required_fields = [
                        "risk_score", "detected_bias", "hallucination_probability",
                        "PII_leaks", "misinformation_flag", "confidence_metrics"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        return TestResult(
                            test_name="Universal Risk Analysis",
                            success=True,
                            response_time_ms=response_time,
                            details={
                                "risk_score": data.get("risk_score"),
                                "pii_detected": data.get("PII_leaks"),
                                "misinformation_detected": data.get("misinformation_flag"),
                                "bias_detected": data.get("detected_bias"),
                                "response_structure_valid": True
                            }
                        )
                    else:
                        return TestResult(
                            test_name="Universal Risk Analysis",
                            success=False,
                            response_time_ms=response_time,
                            details={"missing_fields": missing_fields},
                            error_message=f"Missing required fields: {missing_fields}"
                        )
                else:
                    return TestResult(
                        test_name="Universal Risk Analysis",
                        success=False,
                        response_time_ms=response_time,
                        details={"status_code": response.status},
                        error_message=f"API returned status {response.status}"
                    )
        except Exception as e:
            return TestResult(
                test_name="Universal Risk Analysis",
                success=False,
                response_time_ms=0,
                details={},
                error_message=str(e)
            )
    
    async def test_pii_detection_accuracy(self) -> TestResult:
        """Test 4: PII detection accuracy"""
        logger.info("🔒 Testing PII detection accuracy...")
        
        pii_content = "My SSN is 123-45-6789, credit card 4532-1234-5678-9012, email john@example.com"
        
        payload = {
            "input": pii_content,
            "context": {"source": "pii_test"},
            "config": {"detectors": ["pii"]}
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/risk/analyze",
                json=payload
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    pii_detected = data.get("PII_leaks", False)
                    risk_score = data.get("risk_score", 0)
                    
                    # Should detect PII and have high risk score
                    success = pii_detected and risk_score > 70
                    
                    return TestResult(
                        test_name="PII Detection Accuracy",
                        success=success,
                        response_time_ms=response_time,
                        details={
                            "pii_detected": pii_detected,
                            "risk_score": risk_score,
                            "expected_detection": True
                        }
                    )
                else:
                    return TestResult(
                        test_name="PII Detection Accuracy",
                        success=False,
                        response_time_ms=response_time,
                        details={},
                        error_message=f"API returned status {response.status}"
                    )
        except Exception as e:
            return TestResult(
                test_name="PII Detection Accuracy",
                success=False,
                response_time_ms=0,
                details={},
                error_message=str(e)
            )
    
    async def test_misinformation_detection(self) -> TestResult:
        """Test 5: Misinformation detection"""
        logger.info("📰 Testing misinformation detection...")
        
        fake_news = "BREAKING: Scientists confirm drinking bleach cures all diseases! Share before censored!"
        
        payload = {
            "input": fake_news,
            "context": {"source": "misinformation_test"},
            "config": {"detectors": ["misinformation"]}
        }
        
        start_time = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/risk/analyze",
                json=payload
            ) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    misinformation_detected = data.get("misinformation_flag", False)
                    risk_score = data.get("risk_score", 0)
                    
                    # Should detect misinformation
                    success = misinformation_detected or risk_score > 60
                    
                    return TestResult(
                        test_name="Misinformation Detection",
                        success=success,
                        response_time_ms=response_time,
                        details={
                            "misinformation_detected": misinformation_detected,
                            "risk_score": risk_score,
                            "content_type": "fake_news"
                        }
                    )
                else:
                    return TestResult(
                        test_name="Misinformation Detection",
                        success=False,
                        response_time_ms=response_time,
                        details={},
                        error_message=f"API returned status {response.status}"
                    )
        except Exception as e:
            return TestResult(
                test_name="Misinformation Detection",
                success=False,
                response_time_ms=0,
                details={},
                error_message=str(e)
            )
    
    async def test_performance_benchmarks(self) -> TestResult:
        """Test 6: Performance benchmarks"""
        logger.info("⚡ Testing performance benchmarks...")
        
        # Test concurrent requests
        async def make_request():
            payload = {
                "input": "Performance test content for concurrent analysis",
                "context": {"source": "performance_test"}
            }
            
            start = time.time()
            async with self.session.post(
                f"{self.base_url}/api/v1/risk/analyze",
                json=payload
            ) as response:
                duration = (time.time() - start) * 1000
                return response.status == 200, duration
        
        # Run 20 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (time.time() - start_time) * 1000
        
        # Analyze results
        successful_requests = sum(1 for result in results if isinstance(result, tuple) and result[0])
        avg_response_time = sum(result[1] for result in results if isinstance(result, tuple)) / len(results)
        
        # Performance criteria: >90% success rate, <2000ms average response time
        success = (successful_requests / len(results)) > 0.9 and avg_response_time < 2000
        
        return TestResult(
            test_name="Performance Benchmarks",
            success=success,
            response_time_ms=avg_response_time,
            details={
                "concurrent_requests": len(results),
                "successful_requests": successful_requests,
                "success_rate_percent": (successful_requests / len(results)) * 100,
                "total_time_ms": total_time,
                "avg_response_time_ms": avg_response_time
            }
        )
    
    async def test_multilingual_support(self) -> TestResult:
        """Test 7: Multi-language support"""
        logger.info("🌍 Testing multi-language support...")
        
        results = []
        total_response_time = 0
        
        for content in self.test_data["multilingual_content"]:
            payload = {
                "input": content["text"],
                "context": {"source": "multilingual_test", "language": content["language"]}
            }
            
            start_time = time.time()
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/risk/analyze",
                    json=payload
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    total_response_time += response_time
                    
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            "language": content["language"],
                            "success": True,
                            "risk_score": data.get("risk_score", 0)
                        })
                    else:
                        results.append({
                            "language": content["language"],
                            "success": False,
                            "error": f"Status {response.status}"
                        })
            except Exception as e:
                results.append({
                    "language": content["language"],
                    "success": False,
                    "error": str(e)
                })
        
        successful_languages = sum(1 for r in results if r["success"])
        success = successful_languages >= 2  # At least 2 languages should work
        
        return TestResult(
            test_name="Multi-language Support",
            success=success,
            response_time_ms=total_response_time / len(results),
            details={
                "languages_tested": len(results),
                "successful_languages": successful_languages,
                "results": results
            }
        )
    
    async def test_analytics_endpoints(self) -> TestResult:
        """Test 8: Analytics and monitoring endpoints"""
        logger.info("📊 Testing analytics endpoints...")
        
        endpoints_to_test = [
            "/api/v1/analytics/real-time-metrics",
            "/debug/routes"
        ]
        
        results = {}
        total_response_time = 0
        successful_endpoints = 0
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = (time.time() - start_time) * 1000
                    total_response_time += response_time
                    
                    if response.status == 200:
                        data = await response.json()
                        results[endpoint] = {"success": True, "data_keys": list(data.keys())}
                        successful_endpoints += 1
                    else:
                        results[endpoint] = {"success": False, "status": response.status}
            except Exception as e:
                results[endpoint] = {"success": False, "error": str(e)}
        
        success = successful_endpoints >= 1  # At least one endpoint should work
        
        return TestResult(
            test_name="Analytics Endpoints",
            success=success,
            response_time_ms=total_response_time / len(endpoints_to_test),
            details={
                "endpoints_tested": len(endpoints_to_test),
                "successful_endpoints": successful_endpoints,
                "results": results
            }
        )
    
    async def run_all_tests(self) -> List[TestResult]:
        """Run all system tests"""
        logger.info("🚀 Starting AIRMS complete system test suite...")
        
        await self.setup()
        
        try:
            # Run all tests
            tests = [
                self.test_system_health(),
                self.test_api_documentation(),
                self.test_universal_risk_analysis(),
                self.test_pii_detection_accuracy(),
                self.test_misinformation_detection(),
                self.test_performance_benchmarks(),
                self.test_multilingual_support(),
                self.test_analytics_endpoints()
            ]
            
            self.test_results = await asyncio.gather(*tests)
            
        finally:
            await self.cleanup()
        
        return self.test_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - passed_tests
        
        avg_response_time = sum(result.response_time_ms for result in self.test_results) / total_tests
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate_percent": (passed_tests / total_tests) * 100,
                "avg_response_time_ms": round(avg_response_time, 2)
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "response_time_ms": round(result.response_time_ms, 2),
                    "details": result.details,
                    "error_message": result.error_message
                }
                for result in self.test_results
            ],
            "system_assessment": self._assess_system_health(passed_tests, total_tests, avg_response_time)
        }
        
        return report
    
    def _assess_system_health(self, passed_tests: int, total_tests: int, avg_response_time: float) -> Dict[str, Any]:
        """Assess overall system health"""
        
        success_rate = (passed_tests / total_tests) * 100
        
        if success_rate >= 90 and avg_response_time < 1000:
            status = "EXCELLENT"
            message = "System is performing excellently and ready for production"
        elif success_rate >= 80 and avg_response_time < 2000:
            status = "GOOD"
            message = "System is performing well with minor issues"
        elif success_rate >= 70:
            status = "FAIR"
            message = "System has some issues that should be addressed"
        else:
            status = "POOR"
            message = "System has significant issues requiring immediate attention"
        
        return {
            "status": status,
            "message": message,
            "recommendations": self._get_recommendations(success_rate, avg_response_time)
        }
    
    def _get_recommendations(self, success_rate: float, avg_response_time: float) -> List[str]:
        """Get recommendations based on test results"""
        
        recommendations = []
        
        if success_rate < 90:
            recommendations.append("Review failed tests and fix underlying issues")
        
        if avg_response_time > 1000:
            recommendations.append("Optimize API response times - consider caching and performance tuning")
        
        if success_rate < 80:
            recommendations.append("Conduct thorough system review before production deployment")
        
        recommendations.extend([
            "Monitor system performance continuously",
            "Set up alerting for critical failures",
            "Implement comprehensive logging and monitoring",
            "Regular security audits and updates"
        ])
        
        return recommendations

async def main():
    """Main test execution"""
    
    # Configuration
    base_url = "http://localhost:8000"
    
    print("🧪 AIRMS Universal AI Risk & Misinformation API - Complete System Test")
    print("=" * 80)
    print(f"Testing against: {base_url}")
    print()
    
    # Run tests
    tester = AIRMSSystemTester(base_url)
    results = await tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_report()
    
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {report['test_summary']['total_tests']}")
    print(f"Passed: {report['test_summary']['passed_tests']}")
    print(f"Failed: {report['test_summary']['failed_tests']}")
    print(f"Success Rate: {report['test_summary']['success_rate_percent']:.1f}%")
    print(f"Average Response Time: {report['test_summary']['avg_response_time_ms']:.2f}ms")
    print()
    
    # Individual test results
    print("📋 INDIVIDUAL TEST RESULTS")
    print("-" * 50)
    for result in report['test_results']:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {result['test_name']} ({result['response_time_ms']:.2f}ms)")
        if not result['success'] and result['error_message']:
            print(f"   Error: {result['error_message']}")
    print()
    
    # System assessment
    assessment = report['system_assessment']
    print("🏥 SYSTEM HEALTH ASSESSMENT")
    print("-" * 50)
    print(f"Status: {assessment['status']}")
    print(f"Assessment: {assessment['message']}")
    print()
    
    print("💡 RECOMMENDATIONS")
    print("-" * 50)
    for i, rec in enumerate(assessment['recommendations'], 1):
        print(f"{i}. {rec}")
    print()
    
    # Save detailed report
    with open("airms_system_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("📄 Detailed report saved to: airms_system_test_report.json")
    
    # Exit code based on results
    if report['test_summary']['success_rate_percent'] >= 80:
        print("\n🎉 AIRMS system test completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ AIRMS system test completed with issues!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
