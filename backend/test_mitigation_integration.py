#!/usr/bin/env python3
"""
🧪 AIRMS+ Mitigation Integration Test
Comprehensive test for risk detection + mitigation flow
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.mitigation_service import get_mitigation_service, RiskLevel, RiskType
from app.core.database import startup_database, shutdown_database, get_database_operations

class MitigationIntegrationTest:
    """Integration test suite for mitigation service"""
    
    def __init__(self):
        self.test_results = []
        self.db_ops = None
    
    async def setup(self):
        """Setup test environment"""
        print("🚀 Setting up test environment...")
        try:
            await startup_database()
            self.db_ops = await get_database_operations()
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            raise
    
    async def teardown(self):
        """Cleanup test environment"""
        print("🧹 Cleaning up test environment...")
        try:
            await shutdown_database()
            print("✅ Database connection closed")
        except Exception as e:
            print(f"⚠️ Teardown warning: {e}")
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def test_mitigation_service_initialization(self):
        """Test mitigation service initialization"""
        test_name = "Mitigation Service Initialization"
        try:
            # Check if service is initialized
            mitigation_service = await get_mitigation_service()
            assert mitigation_service is not None, "Service not initialized"
            assert hasattr(mitigation_service, 'strategies'), "Strategies not loaded"
            assert len(mitigation_service.strategies) > 0, "No strategies loaded"
            
            # Check all risk types have strategies
            for risk_type in RiskType:
                assert risk_type in mitigation_service.strategies, f"No strategies for {risk_type}"
                assert len(mitigation_service.strategies[risk_type]) > 0, f"Empty strategies for {risk_type}"
            
            strategy_count = sum(len(strats) for strats in mitigation_service.strategies.values())
            self.log_test_result(test_name, True, f"Service initialized with {strategy_count} strategies")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_risk_report_generation(self):
        """Test risk report generation"""
        test_name = "Risk Report Generation"
        try:
            # Mock risk analysis data
            test_content = "This is a test message containing potential bias and PII like john.doe@email.com"
            risk_analysis = {
                "risk_scores": {
                    "bias": 0.7,
                    "pii": 0.8,
                    "hallucination": 0.2,
                    "adversarial": 0.1,
                    "misinformation": 0.3
                },
                "overall_score": 0.65,
                "detected_risks": ["bias", "pii"]
            }
            
            # Generate risk report
            mitigation_service = await get_mitigation_service()
            report = await mitigation_service.generate_risk_report(
                content=test_content,
                risk_analysis=risk_analysis,
                user_context={"test": True}
            )
            
            # Validate report structure
            assert report.report_id is not None, "Report ID missing"
            assert report.risk_level in RiskLevel, "Invalid risk level"
            assert len(report.risk_types) > 0, "No risk types detected"
            assert report.overall_score == 0.65, "Overall score mismatch"
            assert len(report.mitigation_strategies) > 0, "No mitigation strategies"
            assert len(report.immediate_actions) > 0, "No immediate actions"
            
            self.log_test_result(test_name, True, f"Report generated: {report.report_id}")
            return report
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
            return None
    
    async def test_risk_level_calculation(self):
        """Test risk level calculation logic"""
        test_name = "Risk Level Calculation"
        try:
            # Test different score ranges
            test_cases = [
                (0.9, RiskLevel.CRITICAL),
                (0.7, RiskLevel.HIGH),
                (0.5, RiskLevel.MEDIUM),
                (0.2, RiskLevel.LOW)
            ]
            
            mitigation_service = await get_mitigation_service()
            for score, expected_level in test_cases:
                calculated_level = mitigation_service._calculate_risk_level(score)
                assert calculated_level == expected_level, f"Score {score}: expected {expected_level}, got {calculated_level}"
            
            self.log_test_result(test_name, True, f"All {len(test_cases)} risk level calculations correct")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_mitigation_strategies_retrieval(self):
        """Test mitigation strategies retrieval"""
        test_name = "Mitigation Strategies Retrieval"
        try:
            # Test strategy retrieval for different risk types and levels
            test_cases = [
                ([RiskType.BIAS], RiskLevel.HIGH),
                ([RiskType.PII], RiskLevel.CRITICAL),
                ([RiskType.BIAS, RiskType.PII], RiskLevel.MEDIUM),
                ([RiskType.HALLUCINATION], RiskLevel.LOW)
            ]
            
            mitigation_service = await get_mitigation_service()
            for risk_types, risk_level in test_cases:
                strategies = mitigation_service._get_mitigation_strategies(risk_types, risk_level)
                assert isinstance(strategies, list), "Strategies should be a list"
                assert len(strategies) > 0, f"No strategies for {risk_types} at {risk_level}"
                
                # Validate strategy structure
                for strategy in strategies:
                    assert hasattr(strategy, 'strategy_id'), "Strategy missing ID"
                    assert hasattr(strategy, 'title'), "Strategy missing title"
                    assert hasattr(strategy, 'priority'), "Strategy missing priority"
            
            self.log_test_result(test_name, True, f"Strategy retrieval tested for {len(test_cases)} scenarios")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_compliance_flags_generation(self):
        """Test compliance flags generation"""
        test_name = "Compliance Flags Generation"
        try:
            # Test different risk scenarios
            test_cases = [
                ([RiskType.PII], {"pii": 0.8}, ["GDPR_VIOLATION_RISK", "CCPA_COMPLIANCE_REQUIRED"]),
                ([RiskType.BIAS], {"bias": 0.7}, ["DISCRIMINATION_RISK", "FAIRNESS_AUDIT_REQUIRED"]),
                ([RiskType.MISINFORMATION], {"misinformation": 0.8}, ["CONTENT_ACCURACY_VIOLATION", "FACT_CHECK_REQUIRED"]),
                ([RiskType.ADVERSARIAL], {"adversarial": 0.9}, ["SECURITY_BREACH_RISK", "INCIDENT_RESPONSE_REQUIRED"])
            ]
            
            mitigation_service = await get_mitigation_service()
            for risk_types, risk_scores, expected_flags in test_cases:
                flags = mitigation_service._get_compliance_flags(risk_types, risk_scores)
                assert isinstance(flags, list), "Flags should be a list"
                
                # Check if expected flags are present
                for expected_flag in expected_flags:
                    assert expected_flag in flags, f"Missing expected flag: {expected_flag}"
            
            self.log_test_result(test_name, True, f"Compliance flags tested for {len(test_cases)} scenarios")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_immediate_actions_generation(self):
        """Test immediate actions generation"""
        test_name = "Immediate Actions Generation"
        try:
            # Test different risk levels
            test_cases = [
                (RiskLevel.CRITICAL, [RiskType.PII], ["IMMEDIATE_CONTENT_QUARANTINE", "MASK_SENSITIVE_DATA"]),
                (RiskLevel.HIGH, [RiskType.BIAS], ["FLAG_FOR_MANUAL_REVIEW"]),
                (RiskLevel.MEDIUM, [RiskType.HALLUCINATION], ["ADD_TO_MONITORING_QUEUE"]),
                (RiskLevel.LOW, [RiskType.MISINFORMATION], [])
            ]
            
            mitigation_service = await get_mitigation_service()
            for risk_level, risk_types, expected_actions in test_cases:
                actions = mitigation_service._get_immediate_actions(risk_level, risk_types)
                assert isinstance(actions, list), "Actions should be a list"
                
                # For critical and high risk, ensure actions are present
                if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    assert len(actions) > 0, f"No actions for {risk_level} risk"
            
            self.log_test_result(test_name, True, f"Immediate actions tested for {len(test_cases)} scenarios")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_analytics_summary(self):
        """Test analytics summary generation"""
        test_name = "Analytics Summary"
        try:
            # Generate a test report first
            test_content = "Analytics test content"
            risk_analysis = {
                "risk_scores": {"bias": 0.5, "pii": 0.3},
                "overall_score": 0.4,
                "detected_risks": ["bias"]
            }
            
            mitigation_service = await get_mitigation_service()
            await mitigation_service.generate_risk_report(
                content=test_content,
                risk_analysis=risk_analysis
            )
            
            # Get analytics summary
            analytics = await mitigation_service.get_analytics_summary(days=30)
            
            # Validate analytics structure
            assert isinstance(analytics, dict), "Analytics should be a dict"
            assert "total_reports" in analytics, "Missing total_reports"
            assert "risk_level_distribution" in analytics, "Missing risk_level_distribution"
            assert "risk_type_distribution" in analytics, "Missing risk_type_distribution"
            assert "average_risk_scores" in analytics, "Missing average_risk_scores"
            
            self.log_test_result(test_name, True, f"Analytics generated with {analytics.get('total_reports', 0)} reports")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def test_mongodb_persistence(self):
        """Test MongoDB persistence of risk reports"""
        test_name = "MongoDB Persistence"
        try:
            # Generate a test report
            test_content = "MongoDB persistence test"
            risk_analysis = {
                "risk_scores": {"pii": 0.6},
                "overall_score": 0.6,
                "detected_risks": ["pii"]
            }
            
            mitigation_service = await get_mitigation_service()
            report = await mitigation_service.generate_risk_report(
                content=test_content,
                risk_analysis=risk_analysis
            )
            
            # Verify report was stored in MongoDB
            stored_report = await self.db_ops.find_document(
                collection="risk_reports",
                query={"report_id": report.report_id}
            )
            
            assert stored_report is not None, "Report not found in MongoDB"
            assert stored_report["report_id"] == report.report_id, "Report ID mismatch"
            assert stored_report["risk_level"] == report.risk_level.value, "Risk level mismatch"
            
            self.log_test_result(test_name, True, f"Report {report.report_id} successfully stored and retrieved")
            
        except Exception as e:
            self.log_test_result(test_name, False, str(e))
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting AIRMS+ Mitigation Integration Tests")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests
            await self.test_mitigation_service_initialization()
            await self.test_risk_level_calculation()
            await self.test_mitigation_strategies_retrieval()
            await self.test_compliance_flags_generation()
            await self.test_immediate_actions_generation()
            await self.test_risk_report_generation()
            await self.test_analytics_summary()
            await self.test_mongodb_persistence()
            
        finally:
            await self.teardown()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 Integration Test Complete!")
        return failed_tests == 0

async def main():
    """Main test runner"""
    test_suite = MitigationIntegrationTest()
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    # Run the integration tests
    asyncio.run(main())
