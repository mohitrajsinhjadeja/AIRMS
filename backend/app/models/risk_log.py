"""
📊 Risk Log Model for Chat API Request Logging
Stores every chat API request for dashboard analytics and compliance
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field

class RiskLogDocument(BaseModel):
    """
    Simplified risk log document for every chat API request
    Used for dashboard analytics and compliance tracking
    """
    
    # Primary fields
    _id: Optional[str] = Field(None, alias="_id")
    
    # Request identification
    user_id: Optional[str] = Field(None, description="User ID if available")
    session_id: Optional[str] = Field(None, description="Session ID if available")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    
    # Timestamps
    timestamp: str = Field(..., description="ISO format timestamp")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Creation timestamp")
    
    # Input/Output (masked for safety)
    masked_input: str = Field(..., description="PII-sanitized user input")
    response_length: int = Field(default=0, description="Length of AI response")
    
    # Risk analysis results
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: str = Field(..., description="SAFE, LOW, MEDIUM, HIGH, CRITICAL")
    risk_flags: List[str] = Field(default_factory=list, description="Detected risk categories")
    
    # Processing metadata
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    analysis_version: str = Field(default="3.0", description="Analysis version")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "user_id": "user_123",
                "session_id": "session_456",
                "conversation_id": "48c9e5f5-7a2b-4c8d-9e1f-2a3b4c5d6e7f",
                "timestamp": "2025-09-26T15:30:00.000Z",
                "masked_input": "My sensitive data is [REDACTED]",
                "response_length": 142,
                "risk_score": 65,
                "risk_level": "HIGH",
                "risk_flags": ["PII Detected"]
            }
        }
    
    def to_mongodb_doc(self) -> Dict[str, Any]:
        """Convert to MongoDB document format"""
        doc = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in doc and doc["_id"] is None:
            del doc["_id"]
        return doc
    
    @classmethod
    def from_chat_interaction(cls, interaction_data: Dict[str, Any]) -> 'RiskLogDocument':
        """Create RiskLogDocument from chat interaction data"""
        return cls(
            user_id=interaction_data.get("user_context", {}).get("user_id"),
            session_id=interaction_data.get("session_metadata", {}).get("session_id"),
            conversation_id=interaction_data["conversation_id"],
            timestamp=interaction_data["timestamp"],
            masked_input=interaction_data.get("masked_input", interaction_data["user_message"][:100] + "..." if len(interaction_data["user_message"]) > 100 else interaction_data["user_message"]),
            response_length=len(interaction_data["ai_response"]),
            risk_score=interaction_data["risk_score"],
            risk_level=interaction_data["risk_level"],
            risk_flags=interaction_data["risk_flags"],
            processing_time_ms=interaction_data.get("processing_time_ms"),
            analysis_version=interaction_data.get("analysis_version", "3.0")
        )

class RiskLogRepository:
    """Repository for risk log operations"""
    
    def __init__(self, database):
        self.database = database
        self.collection_name = "risk_logs"
    
    async def save_risk_log(self, interaction_data: Dict[str, Any]) -> str:
        """Save risk log entry to database"""
        try:
            risk_log = RiskLogDocument.from_chat_interaction(interaction_data)
            doc = risk_log.to_mongodb_doc()
            
            collection = self.database[self.collection_name]
            result = await collection.insert_one(doc)
            
            return str(result.inserted_id)
            
        except Exception as e:
            raise Exception(f"Failed to save risk log: {str(e)}")
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent risk logs"""
        try:
            collection = self.database[self.collection_name]
            cursor = collection.find().sort("created_at", -1).limit(limit)
            
            logs = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                logs.append(doc)
            
            return logs
            
        except Exception as e:
            raise Exception(f"Failed to get recent risk logs: {str(e)}")
    
    async def get_dashboard_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard summary statistics"""
        try:
            collection = self.database[self.collection_name]
            
            # Calculate time range
            time_cutoff = datetime.utcnow() - timedelta(hours=hours)
            time_filter = {"timestamp": {"$gte": time_cutoff.isoformat()}}
            
            # Aggregation pipeline
            pipeline = [
                {"$match": time_filter},
                {
                    "$group": {
                        "_id": None,
                        "total_requests": {"$sum": 1},
                        "total_risk_detections": {
                            "$sum": {"$cond": [{"$gt": ["$risk_score", 25]}, 1, 0]}
                        },
                        "average_risk_score": {"$avg": "$risk_score"},
                        "high_risk_requests": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", 75]}, 1, 0]}
                        },
                        "safe_requests": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "SAFE"]}, 1, 0]}
                        },
                        "low_risk_requests": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "LOW"]}, 1, 0]}
                        },
                        "medium_risk_requests": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "MEDIUM"]}, 1, 0]}
                        },
                        "high_risk_requests": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "HIGH"]}, 1, 0]}
                        },
                        "critical_risk_requests": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "CRITICAL"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return {
                    "total_requests": 0,
                    "total_risk_detections": 0,
                    "average_risk_score": 0.0,
                    "high_risk_requests": 0,
                    "timeframe_hours": hours
                }
            
            stats = result[0]
            stats["timeframe_hours"] = hours
            stats.pop("_id", None)
            
            return stats
            
        except Exception as e:
            raise Exception(f"Failed to get dashboard summary: {str(e)}")
    
    async def get_risk_trend(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get risk trend data for specified days"""
        try:
            collection = self.database[self.collection_name]
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Aggregation pipeline for daily trends
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date.isoformat(),
                            "$lt": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": {"$dateFromString": {"dateString": "$timestamp"}}
                            }
                        },
                        "total_requests": {"$sum": 1},
                        "average_risk_score": {"$avg": "$risk_score"},
                        "high_risk_count": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", 75]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await collection.aggregate(pipeline).to_list(None)
            
            # Format results
            trend_data = []
            for result in results:
                trend_data.append({
                    "date": result["_id"],
                    "total_requests": result["total_requests"],
                    "average_risk_score": round(result["average_risk_score"], 1),
                    "high_risk_count": result["high_risk_count"]
                })
            
            return trend_data
            
        except Exception as e:
            raise Exception(f"Failed to get risk trend: {str(e)}")