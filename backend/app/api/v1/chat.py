"""
🤖 Chat API Router - Simple Chatbot with Risk Detection
Provides chat functionality with integrated AI risk assessment
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field

from app.core.database import get_database_operations
from app.core.config import settings
from app.services.ai_integration import AIIntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Pydantic Models
class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    api_key: Optional[str] = Field(None, description="API key for authentication")

class ChatResponse(BaseModel):
    message: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Conversation ID")
    risk_score: float = Field(..., description="Risk score for the conversation")
    risk_flags: List[str] = Field(default_factory=list, description="Risk flags detected")
    timestamp: str = Field(..., description="Response timestamp")

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str
    total_messages: int
    risk_summary: Dict[str, Any]

# Simple API key validation
async def validate_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Validate API key from Authorization header.
    This endpoint requires a valid API key, not an auth token.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. This endpoint requires an API key, not an auth token. Please use the API key dropdown to select a key."
        )
        raise HTTPException(status_code=401, detail="API key required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <api_key>'")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Simple validation - check if it starts with airms_
    if not api_key.startswith("airms_"):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    # TODO: Validate against database
    logger.info(f"🔑 API key validated: {api_key[:8]}...")
    return api_key

# Database Operations
async def get_db_ops():
    """Get database operations instance"""
    return await get_database_operations()

# Chat Endpoints
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db_ops = Depends(get_db_ops),
    api_key: str = Depends(validate_api_key)
) -> ChatResponse:
    """
    🤖 **Chat with AI Assistant**
    
    Send a message to the AI assistant and get a response with risk assessment.
    
    **Features:**
    - AI-powered responses
    - Real-time risk detection
    - Conversation context
    - Risk scoring and flagging
    """
    try:
        logger.info(f"💬 Processing chat message: {request.message[:50]}...")
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Initialize AI response
        ai_response = None
        
        try:
            # Initialize and use AI service with context manager
            async with AIIntegrationService() as ai_service:
                # Get AI response (directly from Gemini)
                system_prompt = """You are an AI Risk Management Assistant, part of the AIRMS (AI Risk Mitigation System). Your role is to:
1. Help users understand and mitigate AI-related risks
2. Provide clear, accurate information about AI safety and ethics
3. Analyze potential risks in AI applications
4. Suggest best practices for responsible AI development
5. Maintain a professional and informative tone

Current context: You are helping users manage and understand AI-related risks. Be direct, informative, and focus on providing actionable insights.

User Query: """
                
                full_prompt = f"{system_prompt}{request.message}"
                ai_response = await ai_service._call_gemini(
                    prompt=full_prompt,
                    max_tokens=2000,  # Increased for more detailed responses
                    temperature=0.7
                )
                
                if not ai_response:
                    raise ValueError("Empty response from Gemini")
                    
        except Exception as e:
            logger.warning(f"Gemini API failed: {e}")
            ai_response = f"I understand you're asking about: '{request.message}'. This is a test response. Please check if GEMINI_API_KEY is configured in settings."
        
        # Perform risk assessment on both user message and AI response
        risk_score = 0.0
        risk_flags = []
        
        try:
            # Simple risk detection for demo
            user_risk_words = ["hack", "attack", "malicious", "exploit", "vulnerability"]
            ai_risk_words = ["dangerous", "harmful", "illegal", "inappropriate"]
            
            # Check user message
            user_message_lower = request.message.lower()
            for word in user_risk_words:
                if word in user_message_lower:
                    risk_score += 0.2
                    risk_flags.append(f"user_input_{word}")
            
            # Check AI response
            ai_response_lower = ai_response.lower()
            for word in ai_risk_words:
                if word in ai_response_lower:
                    risk_score += 0.3
                    risk_flags.append(f"ai_response_{word}")
            
            # Cap risk score at 1.0
            risk_score = min(risk_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Risk assessment failed: {e}")
            risk_score = 0.0
            risk_flags = []
        
        # Store conversation in database
        try:
            conversation_doc = {
                "conversation_id": conversation_id,
                "messages": [
                    {
                        "role": "user",
                        "content": request.message,
                        "timestamp": timestamp
                    },
                    {
                        "role": "assistant", 
                        "content": ai_response,
                        "timestamp": timestamp
                    }
                ],
                "api_key": api_key[:8] + "...",  # Store only preview
                "risk_score": risk_score,
                "risk_flags": risk_flags,
                "created_at": timestamp,
                "updated_at": timestamp
            }
            
            await db_ops.create_document("chat_conversations", conversation_doc)
            logger.info(f"💾 Stored conversation: {conversation_id}")
            
        except Exception as e:
            logger.warning(f"Failed to store conversation: {e}")
        
        # Return response
        response = ChatResponse(
            message=ai_response,
            conversation_id=conversation_id,
            risk_score=risk_score,
            risk_flags=risk_flags,
            timestamp=timestamp
        )
        
        logger.info(f"✅ Chat response generated (risk: {risk_score:.2f})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/conversations", response_model=List[ConversationHistory])
async def get_conversations(
    limit: int = 10,
    skip: int = 0,
    db_ops = Depends(get_db_ops),
    api_key: str = Depends(validate_api_key)
) -> List[ConversationHistory]:
    """
    📜 **Get Chat Conversations**
    
    Retrieve chat conversation history.
    """
    try:
        logger.info(f"📜 Retrieving conversations (limit: {limit}, skip: {skip})")
        
        # Query conversations from database
        query = {"api_key": api_key[:8] + "..."}  # Match API key preview
        sort = [("created_at", -1)]  # Most recent first
        
        conversations_data = await db_ops.find_documents(
            "chat_conversations",
            query,
            limit=limit,
            skip=skip,
            sort=sort
        )
        
        # Convert to response format
        conversations = []
        for conv_data in conversations_data:
            # Convert messages
            messages = []
            for msg in conv_data.get("messages", []):
                messages.append(ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=msg.get("timestamp")
                ))
            
            conversations.append(ConversationHistory(
                conversation_id=conv_data["conversation_id"],
                messages=messages,
                created_at=conv_data["created_at"],
                updated_at=conv_data["updated_at"],
                total_messages=len(messages),
                risk_summary={
                    "risk_score": conv_data.get("risk_score", 0.0),
                    "risk_flags": conv_data.get("risk_flags", [])
                }
            ))
        
        logger.info(f"✅ Retrieved {len(conversations)} conversations")
        return conversations
        
    except Exception as e:
        logger.error(f"❌ Error retrieving conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db_ops = Depends(get_db_ops),
    api_key: str = Depends(validate_api_key)
) -> Dict[str, str]:
    """
    🗑️ **Delete Conversation**
    
    Delete a specific chat conversation.
    """
    try:
        logger.info(f"🗑️ Deleting conversation: {conversation_id}")
        
        # Delete from database
        result = await db_ops.delete_document(
            "chat_conversations",
            {
                "conversation_id": conversation_id,
                "api_key": api_key[:8] + "..."  # Ensure user owns conversation
            }
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"✅ Deleted conversation: {conversation_id}")
        return {"message": f"Conversation {conversation_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

# Test endpoint without authentication
@router.post("/test", response_model=Dict[str, Any])
async def test_chat(request: ChatRequest) -> Dict[str, Any]:
    """
    🧪 **Test Chat (No Auth)**
    
    Test chat functionality without authentication.
    """
    try:
        logger.info(f"🧪 Test chat: {request.message}")
        
        # Simple echo response with timestamp
        response = {
            "status": "success",
            "message": f"Echo: {request.message}",
            "conversation_id": request.conversation_id or str(uuid.uuid4()),
            "risk_score": 0.1,  # Low risk for test
            "risk_flags": [],
            "timestamp": datetime.utcnow().isoformat(),
            "note": "This is a test response without AI integration"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Test chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Test chat failed: {str(e)}")
