from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pymongo import MongoClient
from .risk_detection import RiskAgent
from .sanitizer import InputSanitizer
from .llm_service import LLMService
from .db_connector import DatabaseConnector

class RiskPipeline:
    def __init__(self, mongodb_uri: str, llm_config: Dict[str, Any]):
        self.mongo_client = MongoClient(mongodb_uri)
        self.db = self.mongo_client.airms
        self.risk_agent = RiskAgent()
        self.sanitizer = InputSanitizer()
        self.llm_service = LLMService(llm_config)
        self.db_connector = DatabaseConnector()

    async def process_input(self, 
                          user_input: str, 
                          user_id: str,
                          db_config: Optional[Dict] = None) -> Dict[str, Any]:
        # Generate request ID
        request_id = f"req_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}"
        
        # Step 1: Sanitize input
        safe_input, entities = await self.sanitizer.sanitize_text(user_input)
        
        # Step 2: Detect risks
        risk_results = await self.risk_agent.analyze(safe_input)
        
        # Step 3: Risk score is already computed by risk_agent
        
        # Step 4: Determine mitigation
        mitigation = self._determine_mitigation(risk_results["riskScore"])
        
        # Step 5: Optional DB query
        db_data = None
        if db_config and self._requires_db(safe_input):
            db_data = await self.db_connector.query(db_config, safe_input)
        
        # Step 6: LLM processing
        llm_output = await self.llm_service.process(safe_input, db_data)
        llm_output_sanitized, _ = await self.sanitizer.sanitize_text(llm_output)
        
        # Step 7: Create response
        response = {
            "requestId": request_id,
            "userId": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "input": {
                "original": user_input,
                "sanitized": safe_input,
                "entities": entities
            },
            "risk_assessment": risk_results,
            "mitigation": mitigation,
            "llm_output": {
                "original": llm_output,
                "sanitized": llm_output_sanitized
            }
        }
        
        # Store in MongoDB
        await self._store_request(response)
        
        return response

    def _determine_mitigation(self, risk_score: float) -> Dict[str, Any]:
        if risk_score >= 7.0:
            action = "block"
            reason = "High risk content detected"
        elif risk_score >= 4.0:
            action = "warn"
            reason = "Medium risk content detected"
        else:
            action = "allow"
            reason = "Low risk content"
            
        return {
            "action": action,
            "reason": reason,
            "risk_score": risk_score,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _requires_db(self, input_text: str) -> bool:
        # Add logic to determine if input requires DB access
        db_keywords = ["search", "find", "lookup", "get", "query"]
        return any(keyword in input_text.lower() for keyword in db_keywords)

    async def _store_request(self, request_data: Dict[str, Any]):
        # Store in MongoDB collections
        await self.db.requests.insert_one(request_data)
        
        # Update analytics collection
        analytics_update = {
            "$inc": {
                "totalRequests": 1,
                f"riskLevels.{request_data['mitigation']['action']}": 1
            },
            "$set": {
                "lastUpdated": datetime.utcnow()
            }
        }
        
        await self.db.analytics.update_one(
            {"_id": "global_stats"},
            analytics_update,
            upsert=True
        )