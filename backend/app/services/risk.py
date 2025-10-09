from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.core.config import settings
from packages.risk_detection import RiskAgent

logger = logging.getLogger(__name__)

class RiskService:
    def __init__(self):
        self.risk_agent = RiskAgent()
        self.detectors = {
            "pii": True,
            "bias": True,
            "hallucination": True,
            "adversarial": True,
            "misinformation": True
        }

    async def analyze(
        self, 
        input_text: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze text for various risks using configured detectors
        """
        try:
            # Get active detectors from config or use defaults
            active_detectors = (config or {}).get("detectors", list(self.detectors.keys()))
            
            # Run risk analysis
            result = await self.risk_agent.analyze(
                text=input_text,
                detectors=active_detectors
            )
            
            return {
                "input_hash": hash(input_text),
                "risk_score": result["risk_score"],
                "detectors": result["detectors"],
                "mitigation": result.get("mitigation"),
                "recommendations": result.get("recommendations", []),
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise