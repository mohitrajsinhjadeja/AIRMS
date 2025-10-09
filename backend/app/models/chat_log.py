"""
💬 Chat Log Model for Risk Analytics and Compliance
Stores chat interactions with comprehensive risk analysis data using MongoDB
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator

class ChatLogDocument(BaseModel):
    """
    Chat interaction log document for MongoDB storage with comprehensive risk analytics
    """
    
    # Primary fields
    _id: Optional[str] = Field(None, alias="_id")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    
    # Message content
    user_message: str = Field(..., description="Original user message")
    ai_response: str = Field(..., description="AI assistant response")
    user_message_id: str = Field(..., description="Unique user message ID")
    assistant_message_id: str = Field(..., description="Unique assistant message ID")
    
    # Risk analysis results
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_level: str = Field(..., description="SAFE, LOW, MEDIUM, HIGH, CRITICAL")
    risk_flags: List[str] = Field(default_factory=list, description="Detected risk categories")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Analysis confidence")
    
    # Detailed risk analysis
    input_risk_details: Dict[str, Any] = Field(default_factory=dict, description="Input analysis details")
    output_risk_details: Dict[str, Any] = Field(default_factory=dict, description="Output analysis details")
    scoring_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Points breakdown")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")
    
    # Metadata
    timestamp: str = Field(..., description="ISO format timestamp")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    analysis_version: str = Field(default="3.0_deterministic", description="Analysis version")
    system_prompt_used: bool = Field(default=True, description="Whether system prompt was used")
    deterministic_scoring: bool = Field(default=True, description="Whether deterministic scoring was used")
    
    # Context information
    user_context: Dict[str, Any] = Field(default_factory=dict, description="User context data")
    session_metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    
    # Audit fields
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Creation timestamp")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Update timestamp")
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "conversation_id": "48c9e5f5-7a2b-4c8d-9e1f-2a3b4c5d6e7f",
                "user_message": "My Aadhaar number is 1234-5678-9876",
                "ai_response": "For your safety, I cannot process Aadhaar numbers...",
                "user_message_id": "msg_user_123",
                "assistant_message_id": "msg_ai_456",
                "risk_score": 65,
                "risk_level": "HIGH",
                "risk_flags": ["PII Detected"],
                "confidence_score": 0.92,
                "timestamp": "2025-09-26T15:30:00.000Z",
                "analysis_version": "3.0_deterministic"
            }
        }
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        """Ensure risk level is valid"""
        valid_levels = ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")
        return v
    
    def to_mongodb_doc(self) -> Dict[str, Any]:
        """Convert to MongoDB document format"""
        doc = self.dict(by_alias=True, exclude_unset=True)
        if "_id" in doc and doc["_id"] is None:
            del doc["_id"]
        return doc
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get condensed risk summary for dashboard"""
        return {
            "conversation_id": self.conversation_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "risk_flags": self.risk_flags,
            "timestamp": self.timestamp,
            "confidence": self.confidence_score
        }
    
    @classmethod
    def from_interaction_data(cls, interaction_data: Dict[str, Any]) -> 'ChatLogDocument':
        """Create ChatLogDocument from interaction data"""
        detailed_analysis = interaction_data.get("detailed_risk_analysis", {})
        
        return cls(
            conversation_id=interaction_data["conversation_id"],
            user_message=interaction_data["user_message"],
            ai_response=interaction_data["ai_response"],
            user_message_id=interaction_data["user_message_id"],
            assistant_message_id=interaction_data["assistant_message_id"],
            risk_score=interaction_data["risk_score"],
            risk_level=interaction_data["risk_level"],
            risk_flags=interaction_data["risk_flags"],
            confidence_score=detailed_analysis.get("confidence", 0.8),
            input_risk_details=detailed_analysis.get("input_risks", {}),
            output_risk_details=detailed_analysis.get("output_risks", {}),
            scoring_breakdown=detailed_analysis.get("scoring_breakdown", {}),
            recommendations=detailed_analysis.get("recommendations", []),
            timestamp=interaction_data["timestamp"],
            processing_time_ms=interaction_data.get("processing_time_ms"),
            user_context=interaction_data.get("user_context", {}),
            session_metadata=interaction_data.get("session_metadata", {})
        )

class ChatAnalyticsDocument(BaseModel):
    """
    Daily chat analytics aggregation document for MongoDB
    """
    
    _id: Optional[str] = Field(None, alias="_id")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    
    # Daily statistics
    total_chats: int = Field(default=0, description="Total chat interactions")
    total_risk_detections: int = Field(default=0, description="Total risk detections")
    average_risk_score: float = Field(default=0.0, description="Average risk score")
    blocked_messages: int = Field(default=0, description="Number of blocked messages")
    
    # Risk distribution
    safe_count: int = Field(default=0, description="Safe interactions")
    low_risk_count: int = Field(default=0, description="Low risk interactions")
    medium_risk_count: int = Field(default=0, description="Medium risk interactions")
    high_risk_count: int = Field(default=0, description="High risk interactions")
    critical_risk_count: int = Field(default=0, description="Critical risk interactions")
    
    # Risk category counts
    pii_detections: int = Field(default=0, description="PII detection count")
    bias_detections: int = Field(default=0, description="Bias detection count")
    adversarial_detections: int = Field(default=0, description="Adversarial detection count")
    toxicity_detections: int = Field(default=0, description="Toxicity detection count")
    
    # Audit fields
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    class Config:
        allow_population_by_field_name = True
    
    def to_dashboard_format(self) -> Dict[str, Any]:
        """Convert analytics to dashboard format"""
        total_interactions = max(self.total_chats, 1)  # Prevent division by zero
        
        return {
            "date": self.date,
            "overview": {
                "total_chats": self.total_chats,
                "total_risk_detections": self.total_risk_detections,
                "average_risk_score": round(self.average_risk_score, 1),
                "blocked_messages": self.blocked_messages
            },
            "risk_distribution": {
                "safe": {"count": self.safe_count, "percentage": round((self.safe_count / total_interactions) * 100, 1)},
                "low_risk": {"count": self.low_risk_count, "percentage": round((self.low_risk_count / total_interactions) * 100, 1)},
                "medium_risk": {"count": self.medium_risk_count, "percentage": round((self.medium_risk_count / total_interactions) * 100, 1)},
                "high_risk": {"count": self.high_risk_count, "percentage": round((self.high_risk_count / total_interactions) * 100, 1)},
                "critical_risk": {"count": self.critical_risk_count, "percentage": round((self.critical_risk_count / total_interactions) * 100, 1)}
            },
            "risk_categories": {
                "pii_detections": self.pii_detections,
                "bias_detections": self.bias_detections,
                "adversarial_detections": self.adversarial_detections,
                "toxicity_detections": self.toxicity_detections
            }
        }

class ChatLogRepository:
    """Repository for chat log operations"""
    
    def __init__(self, database):
        self.database = database
        self.collection_name = "chat_logs"
        self.analytics_collection_name = "chat_analytics"
    
    async def save_chat_interaction(self, interaction_data: Dict[str, Any]) -> str:
        """Save chat interaction to database"""
        try:
            chat_log = ChatLogDocument.from_interaction_data(interaction_data)
            doc = chat_log.to_mongodb_doc()
            
            collection = self.database[self.collection_name]
            result = await collection.insert_one(doc)
            
            return str(result.inserted_id)
            
        except Exception as e:
            raise Exception(f"Failed to save chat interaction: {str(e)}")
    
    async def get_recent_chats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent chat interactions"""
        try:
            collection = self.database[self.collection_name]
            cursor = collection.find().sort("created_at", -1).limit(limit)
            
            chats = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                chats.append(doc)
            
            return chats
            
        except Exception as e:
            raise Exception(f"Failed to get recent chats: {str(e)}")
    
    async def get_risk_statistics(self) -> Dict[str, Any]:
        """Get aggregated risk statistics"""
        try:
            collection = self.database[self.collection_name]
            
            # Aggregation pipeline for risk statistics
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_chats": {"$sum": 1},
                        "total_risk_detections": {
                            "$sum": {"$cond": [{"$gt": ["$risk_score", 0]}, 1, 0]}
                        },
                        "average_risk_score": {"$avg": "$risk_score"},
                        "blocked_messages": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", 75]}, 1, 0]}
                        },
                        "safe_count": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "SAFE"]}, 1, 0]}
                        },
                        "low_risk_count": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "LOW"]}, 1, 0]}
                        },
                        "medium_risk_count": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "MEDIUM"]}, 1, 0]}
                        },
                        "high_risk_count": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "HIGH"]}, 1, 0]}
                        },
                        "critical_risk_count": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "CRITICAL"]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if not result:
                return {
                    "total_chats": 0,
                    "total_risk_detections": 0,
                    "average_risk_score": 0.0,
                    "blocked_messages": 0
                }
            
            return result[0]
            
        except Exception as e:
            raise Exception(f"Failed to get risk statistics: {str(e)}")