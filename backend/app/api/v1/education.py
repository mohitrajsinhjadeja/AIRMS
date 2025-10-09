"""
🎓 Educational Content API Endpoints
Generate educational content for misinformation detection and digital literacy
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.core.auth import get_current_user
from app.models.user import UserInDB
from app.services.educational_content import (
    educational_content_service, 
    generate_misinformation_explanation,
    generate_fact_checking_guide,
    generate_bias_awareness_content,
    ContentType,
    DifficultyLevel
)
from app.core.database import get_database_operations
from app.schemas.base import BaseResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/education", tags=["Educational Content"])

# Request Models
class MisinformationExplanationRequest(BaseModel):
    topic: str = Field(..., description="Topic or claim to explain")
    detected_issues: List[str] = Field(..., description="List of detected misinformation issues")
    difficulty_level: str = Field("intermediate", description="Target difficulty level: beginner, intermediate, advanced")
    save_to_library: bool = Field(True, description="Save to educational content library")

class FactCheckGuideRequest(BaseModel):
    content_category: str = Field(..., description="Content category (health, politics, technology, social)")
    difficulty_level: str = Field("intermediate", description="Target difficulty level")
    include_exercises: bool = Field(True, description="Include practice exercises")
    cultural_context: str = Field("indian", description="Cultural context for examples")

class BiasAwarenessRequest(BaseModel):
    bias_types: List[str] = Field(..., description="Types of biases to address")
    cultural_context: str = Field("indian", description="Cultural context for examples")
    difficulty_level: str = Field("intermediate", description="Target difficulty level")
    include_interactive: bool = Field(True, description="Include interactive elements")

class ContentLibraryRequest(BaseModel):
    content_type: Optional[str] = Field(None, description="Filter by content type")
    difficulty_level: Optional[str] = Field(None, description="Filter by difficulty level")
    topic: Optional[str] = Field(None, description="Search by topic")
    limit: int = Field(20, description="Maximum results", ge=1, le=100)
    offset: int = Field(0, description="Offset for pagination", ge=0)

# Response Models
class EducationalContentResponse(BaseModel):
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Educational content in markdown format")
    content_type: str = Field(..., description="Type of educational content")
    difficulty_level: str = Field(..., description="Difficulty level")
    key_points: List[str] = Field(..., description="Key learning points")
    examples: List[Dict[str, Any]] = Field(..., description="Relevant examples")
    interactive_elements: List[Dict[str, Any]] = Field(..., description="Interactive learning elements")
    sources: List[str] = Field(..., description="Educational sources and references")
    metadata: Dict[str, Any] = Field(..., description="Content metadata")

class ContentLibraryResponse(BaseModel):
    content_id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    content_type: str = Field(..., description="Type of content")
    difficulty_level: str = Field(..., description="Difficulty level")
    topic: str = Field(..., description="Main topic")
    created_at: str = Field(..., description="Creation timestamp")
    usage_count: int = Field(..., description="Number of times accessed")
    rating: Optional[float] = Field(None, description="User rating")

class ContentStatsResponse(BaseModel):
    total_content: int = Field(..., description="Total content items")
    content_by_type: Dict[str, int] = Field(..., description="Content distribution by type")
    content_by_difficulty: Dict[str, int] = Field(..., description="Content distribution by difficulty")
    popular_topics: List[Dict[str, Any]] = Field(..., description="Most popular topics")
    recent_activity: Dict[str, Any] = Field(..., description="Recent content activity")

@router.post("/explain-misinformation", response_model=EducationalContentResponse)
async def create_misinformation_explanation(
    request: MisinformationExplanationRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    🎓 Generate Misinformation Explanation
    
    Creates comprehensive educational content explaining why specific information
    is considered misinformation, including detection techniques and fact-checking guidance.
    """
    try:
        logger.info(f"🎓 Generating misinformation explanation for topic: {request.topic}")
        
        # Generate educational content
        content = await generate_misinformation_explanation(
            topic=request.topic,
            detected_issues=request.detected_issues,
            difficulty_level=request.difficulty_level
        )
        
        # Save to library if requested
        if request.save_to_library:
            background_tasks.add_task(
                _save_to_content_library,
                content,
                str(current_user.id),
                request.topic
            )
        
        # Convert to response format
        response = EducationalContentResponse(
            title=content.title,
            content=content.content,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            key_points=content.key_points,
            examples=content.examples,
            interactive_elements=content.interactive_elements,
            sources=content.sources,
            metadata=content.metadata
        )
        
        logger.info(f"✅ Misinformation explanation generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate misinformation explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/fact-check-guide", response_model=EducationalContentResponse)
async def create_fact_check_guide(
    request: FactCheckGuideRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    🔍 Generate Fact-Checking Guide
    
    Creates comprehensive fact-checking methodology guides for specific content categories,
    including step-by-step processes, tools, and practice exercises.
    """
    try:
        logger.info(f"🔍 Generating fact-checking guide for category: {request.content_category}")
        
        # Generate fact-checking guide
        content = await generate_fact_checking_guide(
            content_category=request.content_category,
            difficulty_level=request.difficulty_level
        )
        
        # Enhance with cultural context if specified
        if request.cultural_context != "general":
            content.metadata["cultural_context"] = request.cultural_context
            # Add cultural context to examples and tools
            content = await _enhance_with_cultural_context(content, request.cultural_context)
        
        # Save to library
        background_tasks.add_task(
            _save_to_content_library,
            content,
            str(current_user.id),
            f"fact_checking_{request.content_category}"
        )
        
        response = EducationalContentResponse(
            title=content.title,
            content=content.content,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            key_points=content.key_points,
            examples=content.examples,
            interactive_elements=content.interactive_elements,
            sources=content.sources,
            metadata=content.metadata
        )
        
        logger.info(f"✅ Fact-checking guide generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate fact-checking guide: {e}")
        raise HTTPException(status_code=500, detail=f"Guide generation failed: {str(e)}")

@router.post("/bias-awareness", response_model=EducationalContentResponse)
async def create_bias_awareness_content(
    request: BiasAwarenessRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    🧠 Generate Bias Awareness Content
    
    Creates educational content focused on recognizing and mitigating various types of bias
    in information, with culturally relevant examples and interactive exercises.
    """
    try:
        logger.info(f"🧠 Generating bias awareness content for types: {request.bias_types}")
        
        # Generate bias awareness content
        content = await generate_bias_awareness_content(
            bias_types=request.bias_types,
            cultural_context=request.cultural_context,
            difficulty_level=request.difficulty_level
        )
        
        # Save to library
        background_tasks.add_task(
            _save_to_content_library,
            content,
            str(current_user.id),
            f"bias_awareness_{'-'.join(request.bias_types)}"
        )
        
        response = EducationalContentResponse(
            title=content.title,
            content=content.content,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            key_points=content.key_points,
            examples=content.examples,
            interactive_elements=content.interactive_elements,
            sources=content.sources,
            metadata=content.metadata
        )
        
        logger.info(f"✅ Bias awareness content generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to generate bias awareness content: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.get("/library", response_model=List[ContentLibraryResponse])
async def get_content_library(
    request: ContentLibraryRequest = Depends(),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    📚 Educational Content Library
    
    Browse and search the educational content library with filtering and pagination.
    """
    try:
        db_ops = await get_database_operations()
        
        # Build query filter
        query_filter = {}
        
        # Filter by user (users see their own content + public content)
        query_filter['$or'] = [
            {'user_id': str(current_user.id)},
            {'is_public': True}
        ]
        
        # Apply additional filters
        if request.content_type:
            query_filter['content_type'] = request.content_type
        
        if request.difficulty_level:
            query_filter['difficulty_level'] = request.difficulty_level
        
        if request.topic:
            query_filter['$text'] = {'$search': request.topic}
        
        # Execute query with pagination
        cursor = db_ops.db.educational_content.find(query_filter).sort('created_at', -1)
        
        if request.offset > 0:
            cursor = cursor.skip(request.offset)
        
        cursor = cursor.limit(request.limit)
        
        results = await cursor.to_list(length=request.limit)
        
        # Convert to response format
        library_items = []
        for result in results:
            library_items.append(ContentLibraryResponse(
                content_id=str(result['_id']),
                title=result['title'],
                content_type=result['content_type'],
                difficulty_level=result['difficulty_level'],
                topic=result['topic'],
                created_at=result['created_at'].isoformat(),
                usage_count=result.get('usage_count', 0),
                rating=result.get('rating')
            ))
        
        logger.info(f"📚 Retrieved {len(library_items)} content items from library")
        return library_items
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve content library: {e}")
        raise HTTPException(status_code=500, detail=f"Library retrieval failed: {str(e)}")

@router.get("/library/{content_id}", response_model=EducationalContentResponse)
async def get_content_by_id(
    content_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    📖 Get Specific Educational Content
    
    Retrieve specific educational content by ID and increment usage counter.
    """
    try:
        from bson import ObjectId
        
        db_ops = await get_database_operations()
        
        # Find content by ID
        content = await db_ops.db.educational_content.find_one({
            '_id': ObjectId(content_id),
            '$or': [
                {'user_id': str(current_user.id)},
                {'is_public': True}
            ]
        })
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Increment usage counter
        await db_ops.db.educational_content.update_one(
            {'_id': ObjectId(content_id)},
            {'$inc': {'usage_count': 1}}
        )
        
        # Convert to response format
        response = EducationalContentResponse(
            title=content['title'],
            content=content['content'],
            content_type=content['content_type'],
            difficulty_level=content['difficulty_level'],
            key_points=content['key_points'],
            examples=content['examples'],
            interactive_elements=content['interactive_elements'],
            sources=content['sources'],
            metadata=content['metadata']
        )
        
        logger.info(f"📖 Retrieved content: {content['title']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve content: {e}")
        raise HTTPException(status_code=500, detail=f"Content retrieval failed: {str(e)}")

@router.get("/statistics", response_model=ContentStatsResponse)
async def get_content_statistics(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    📊 Educational Content Statistics
    
    Get comprehensive statistics about educational content usage and trends.
    """
    try:
        db_ops = await get_database_operations()
        
        # Base query for user's accessible content
        base_query = {
            '$or': [
                {'user_id': str(current_user.id)},
                {'is_public': True}
            ]
        }
        
        # Get total content count
        total_content = await db_ops.db.educational_content.count_documents(base_query)
        
        # Get content distribution by type
        type_pipeline = [
            {'$match': base_query},
            {'$group': {'_id': '$content_type', 'count': {'$sum': 1}}}
        ]
        type_results = await db_ops.db.educational_content.aggregate(type_pipeline).to_list(length=None)
        content_by_type = {result['_id']: result['count'] for result in type_results}
        
        # Get content distribution by difficulty
        difficulty_pipeline = [
            {'$match': base_query},
            {'$group': {'_id': '$difficulty_level', 'count': {'$sum': 1}}}
        ]
        difficulty_results = await db_ops.db.educational_content.aggregate(difficulty_pipeline).to_list(length=None)
        content_by_difficulty = {result['_id']: result['count'] for result in difficulty_results}
        
        # Get popular topics
        topic_pipeline = [
            {'$match': base_query},
            {'$group': {'_id': '$topic', 'count': {'$sum': 1}, 'total_usage': {'$sum': '$usage_count'}}},
            {'$sort': {'total_usage': -1}},
            {'$limit': 10}
        ]
        topic_results = await db_ops.db.educational_content.aggregate(topic_pipeline).to_list(length=10)
        popular_topics = [
            {
                'topic': result['_id'],
                'content_count': result['count'],
                'total_usage': result['total_usage']
            }
            for result in topic_results
        ]
        
        # Get recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_activity = {
            'new_content_last_7_days': await db_ops.db.educational_content.count_documents({
                **base_query,
                'created_at': {'$gte': week_ago}
            }),
            'total_usage_last_7_days': await db_ops.db.educational_content.aggregate([
                {'$match': {**base_query, 'last_accessed': {'$gte': week_ago}}},
                {'$group': {'_id': None, 'total_usage': {'$sum': '$usage_count'}}}
            ]).to_list(length=1)
        }
        
        # Extract total usage from aggregation result
        if recent_activity['total_usage_last_7_days']:
            recent_activity['total_usage_last_7_days'] = recent_activity['total_usage_last_7_days'][0]['total_usage']
        else:
            recent_activity['total_usage_last_7_days'] = 0
        
        response = ContentStatsResponse(
            total_content=total_content,
            content_by_type=content_by_type,
            content_by_difficulty=content_by_difficulty,
            popular_topics=popular_topics,
            recent_activity=recent_activity
        )
        
        logger.info(f"📊 Retrieved content statistics for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to get content statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.post("/library/{content_id}/rate")
async def rate_content(
    content_id: str,
    rating: float,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    ⭐ Rate Educational Content
    
    Provide a rating for educational content to help improve quality and recommendations.
    Rating should be between 1.0 and 5.0.
    """
    try:
        if rating < 1.0 or rating > 5.0:
            raise HTTPException(status_code=400, detail="Rating should be between 1.0 and 5.0")
        
        from bson import ObjectId
        
        db_ops = await get_database_operations()
        
        # Check if content exists and user has access
        content = await db_ops.db.educational_content.find_one({
            '_id': ObjectId(content_id),
            '$or': [
                {'user_id': str(current_user.id)},
                {'is_public': True}
            ]
        })
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Update or add rating
        current_ratings = content.get('ratings', [])
        user_rating_index = next((i for i, r in enumerate(current_ratings) if r['user_id'] == str(current_user.id)), None)
        
        if user_rating_index is not None:
            # Update existing rating
            current_ratings[user_rating_index]['rating'] = rating
            current_ratings[user_rating_index]['updated_at'] = datetime.utcnow()
        else:
            # Add new rating
            current_ratings.append({
                'user_id': str(current_user.id),
                'rating': rating,
                'created_at': datetime.utcnow()
            })
        
        # Calculate average rating
        avg_rating = sum(r['rating'] for r in current_ratings) / len(current_ratings)
        
        # Update content with new ratings
        await db_ops.db.educational_content.update_one(
            {'_id': ObjectId(content_id)},
            {
                '$set': {
                    'ratings': current_ratings,
                    'rating': round(avg_rating, 2)
                }
            }
        )
        
        logger.info(f"⭐ Content {content_id} rated {rating} by user {current_user.id}")
        return {"message": "Rating submitted successfully", "average_rating": round(avg_rating, 2)}
        
    except Exception as e:
        logger.error(f"❌ Failed to rate content: {e}")
        raise HTTPException(status_code=500, detail=f"Rating submission failed: {str(e)}")

# Background task functions
async def _save_to_content_library(content, user_id: str, topic: str):
    """Save educational content to the library"""
    try:
        db_ops = await get_database_operations()
        
        content_doc = {
            'user_id': user_id,
            'title': content.title,
            'content': content.content,
            'content_type': content.content_type.value,
            'difficulty_level': content.difficulty_level.value,
            'topic': topic,
            'key_points': content.key_points,
            'examples': content.examples,
            'interactive_elements': content.interactive_elements,
            'sources': content.sources,
            'metadata': content.metadata,
            'usage_count': 0,
            'ratings': [],
            'is_public': False,  # Private by default
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow()
        }
        
        await db_ops.db.educational_content.insert_one(content_doc)
        logger.info(f"📚 Saved educational content to library: {content.title}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save content to library: {e}")

async def _enhance_with_cultural_context(content, cultural_context: str):
    """Enhance content with cultural context"""
    try:
        # Add cultural context to metadata
        content.metadata['cultural_context'] = cultural_context
        
        # Add culturally relevant examples if Indian context
        if cultural_context.lower() == "indian":
            indian_examples = [
                {
                    "title": "Example: WhatsApp Misinformation in India",
                    "description": "How misinformation spreads through WhatsApp groups and family networks",
                    "red_flags": ["Forwarded messages", "Emotional content", "Lack of original source"],
                    "fact_check_approach": "Check with PIB Fact Check, Boom Live, Alt News"
                },
                {
                    "title": "Example: Regional Language Misinformation",
                    "description": "False information in regional languages that's harder to fact-check",
                    "red_flags": ["Language barriers", "Limited fact-checking resources", "Cultural sensitivities"],
                    "fact_check_approach": "Use Google Translate, consult local experts, check regional fact-checkers"
                }
            ]
            
            # Add to existing examples
            content.examples.extend(indian_examples[:2])  # Add up to 2 Indian examples
        
        return content
        
    except Exception as e:
        logger.error(f"❌ Failed to enhance content with cultural context: {e}")
        return content

@router.get("/topics")
async def get_education_topics() -> BaseResponse:
    """Get educational topics"""
    return BaseResponse(
        success=True,
        message="Topics retrieved",
        data={
            "topics": [
                "digital_literacy",
                "misinformation_detection", 
                "privacy_protection",
                "ai_safety"
            ]
        }
    )
