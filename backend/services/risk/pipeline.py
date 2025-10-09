from typing import Dict, Any
from core.config import get_settings
from detectors import PIIDetector, BiasDetector, HallucinationDetector
from utils.sanitizers import InputSanitizer
from services.llm import LLMService
from services.audit import AuditLogger

class RiskPipeline:
    def __init__(self):
        self.settings = get_settings()
        self.detectors = {
            "pii": PIIDetector(),
            "bias": BiasDetector(),
            "hallucination": HallucinationDetector()
        }
        self.sanitizer = InputSanitizer()
        self.llm_service = LLMService()
        self.audit = AuditLogger()
    
    async def process(self, 
                     user_input: str, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        # Pipeline implementation
        audit_context = {"request_id": context["request_id"]}
        
        try:
            # Step 1: Sanitize Input
            safe_input = await self.sanitizer.sanitize(user_input)
            await self.audit.log("input_sanitized", audit_context)
            
            # Step 2: Risk Detection
            risk_results = await self._run_detectors(safe_input)
            await self.audit.log("risks_detected", audit_context)
            
            # Step 3: LLM Processing
            if self._should_process_llm(risk_results):
                llm_response = await self.llm_service.process(safe_input)
                safe_output = await self.sanitizer.sanitize(llm_response)
            else:
                safe_output = None
            
            # Step 4: Final Response
            response = self._build_response(
                safe_input=safe_input,
                risk_results=risk_results,
                safe_output=safe_output,
                context=context
            )
            
            await self.audit.log("request_completed", audit_context)
            return response
            
        except Exception as e:
            await self.audit.log("error", {**audit_context, "error": str(e)})
            raise