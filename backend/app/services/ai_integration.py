"""
🛡️ AIRMS+ AI Integration Service
Intelligent routing between Groq (fast filtering) and Gemini (deep reasoning)
"""

import asyncio
import logging
import random
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import aiohttp
import json
from datetime import datetime

from app.core.config import settings, get_ai_routing_config

# Configure logging
logger = logging.getLogger(__name__)

class AITaskType(Enum):
    """AI task types for intelligent routing"""
    FAST_FILTER = "fast_filter"          # Groq - Quick bias, PII, adversarial detection
    DEEP_REASONING = "deep_reasoning"     # Gemini - Complex analysis, explanations
    MISINFORMATION = "misinformation"     # Gemini - Fact-checking, context analysis
    EDUCATION = "education"               # Gemini - Educational content generation
    QUICK_SCORING = "quick_scoring"       # Groq - Fast risk scoring

class AIProvider(Enum):
    """AI providers"""
    GROQ = "groq"
    GEMINI = "gemini"
    LOCAL = "local"

class AIIntegrationService:
    """
    Intelligent AI routing service for cost optimization and quality
    Routes 80% traffic to Groq (fast/cheap) and 20% to Gemini (deep reasoning)
    """
    
    def __init__(self):
        self.routing_config = get_ai_routing_config()
        
        # API endpoints
        self.groq_endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self.gemini_endpoint = f"https://generativelanguage.googleapis.com/v1/models/{settings.GEMINI_MODEL}:generateContent"
        
        # Initialize HTTP session
        self.session = aiohttp.ClientSession()
        
        # Request statistics
        self.stats = {
            "total_requests": 0,
            "groq_requests": 0,
            "gemini_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _should_use_groq(self, task_type: AITaskType) -> bool:
        """Determine if task should use Groq based on routing strategy"""
        # Check if task type is in Groq's preferred list
        if task_type.value in self.routing_config["use_groq_for"]:
            return True
        
        # Check if task type is in Gemini's preferred list
        if task_type.value in self.routing_config["use_gemini_for"]:
            return False
        
        # Use percentage-based routing for other tasks
        return random.randint(1, 100) <= self.routing_config["groq_percentage"]
    
    async def process_request(self, 
                            task_type: AITaskType,
                            prompt: str,
                            context: Optional[Dict[str, Any]] = None,
                            max_tokens: Optional[int] = None,
                            temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Process AI request with intelligent routing
        """
        start_time = datetime.utcnow()
        self.stats["total_requests"] += 1
        
        try:
            # Determine which AI to use
            use_groq = self._should_use_groq(task_type)
            provider = AIProvider.GROQ if use_groq else AIProvider.GEMINI
            
            # Route to appropriate AI
            if provider == AIProvider.GROQ:
                result = await self._call_groq(prompt, max_tokens, temperature)
                self.stats["groq_requests"] += 1
            else:
                result = await self._call_gemini(prompt, max_tokens, temperature)
                self.stats["gemini_requests"] += 1
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_avg_response_time(response_time)
            
            return {
                "success": True,
                "provider": provider.value,
                "task_type": task_type.value,
                "response": result,
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"AI request failed: {e}")
            
            # Try fallback provider
            try:
                fallback_provider = AIProvider.GEMINI if use_groq else AIProvider.GROQ
                logger.info(f"Trying fallback provider: {fallback_provider.value}")
                
                if fallback_provider == AIProvider.GROQ:
                    result = await self._call_groq(prompt, max_tokens, temperature)
                else:
                    result = await self._call_gemini(prompt, max_tokens, temperature)
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                self._update_avg_response_time(response_time)
                
                return {
                    "success": True,
                    "provider": fallback_provider.value,
                    "task_type": task_type.value,
                    "response": result,
                    "response_time": response_time,
                    "fallback_used": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return {
                    "success": False,
                    "error": str(e),
                    "fallback_error": str(fallback_error),
                    "task_type": task_type.value,
                    "timestamp": datetime.utcnow().isoformat()
                }
    
    async def _call_groq(self, 
                        prompt: str, 
                        max_tokens: Optional[int] = None,
                        temperature: Optional[float] = None) -> str:
        """Call Groq API for fast processing"""
        if not settings.GROQ_API_KEY:
            raise ValueError("Groq API key not configured")
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens or settings.GROQ_MAX_TOKENS,
            "temperature": temperature or settings.GROQ_TEMPERATURE
        }
        
        async with self.session.post(self.groq_endpoint, headers=headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Groq API error {response.status}: {error_text}")
            
            data = await response.json()
            return data["choices"][0]["message"]["content"]
    
    async def __aenter__(self):
        """Async context manager entry"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _call_gemini(self, 
                          prompt: str, 
                          max_tokens: Optional[int] = None,
                          temperature: Optional[float] = None) -> str:
        """Call Gemini API for deep reasoning"""
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        url = f"{self.gemini_endpoint}?key={settings.GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens or settings.GEMINI_MAX_TOKENS,
                "temperature": temperature or settings.GEMINI_TEMPERATURE
            }
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Gemini API error {response.status}: {error_text}")
            
            data = await response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time"""
        if self.stats["total_requests"] == 1:
            self.stats["avg_response_time"] = response_time
        else:
            # Calculate running average
            total = self.stats["avg_response_time"] * (self.stats["total_requests"] - 1)
            self.stats["avg_response_time"] = (total + response_time) / self.stats["total_requests"]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI service statistics"""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "groq_percentage": (self.stats["groq_requests"] / total) * 100,
            "gemini_percentage": (self.stats["gemini_requests"] / total) * 100,
            "success_rate": ((total - self.stats["failed_requests"]) / total) * 100,
            "routing_config": self.routing_config
        }

class FactCheckingService:
    """External fact-checking API integration"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints
        self.google_factcheck_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.wikipedia_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def check_claim(self, claim: str) -> Dict[str, Any]:
        """Check claim against multiple fact-checking sources"""
        results = {
            "claim": claim,
            "sources_checked": [],
            "fact_check_results": [],
            "confidence_score": 0.0,
            "verdict": "unknown"
        }
        
        # Check Google Fact Check API
        if settings.GOOGLE_FACT_CHECK_ENABLED and settings.GOOGLE_FACT_CHECK_API_KEY:
            try:
                google_result = await self._check_google_factcheck(claim)
                if google_result:
                    results["sources_checked"].append("google_factcheck")
                    results["fact_check_results"].append(google_result)
            except Exception as e:
                logger.warning(f"Google Fact Check failed: {e}")
        
        # Check NewsAPI for related articles
        if settings.NEWSAPI_ENABLED and settings.NEWSAPI_KEY:
            try:
                news_result = await self._check_newsapi(claim)
                if news_result:
                    results["sources_checked"].append("newsapi")
                    results["fact_check_results"].append(news_result)
            except Exception as e:
                logger.warning(f"NewsAPI check failed: {e}")
        
        # Check Wikipedia
        if settings.WIKIPEDIA_ENABLED:
            try:
                wiki_result = await self._check_wikipedia(claim)
                if wiki_result:
                    results["sources_checked"].append("wikipedia")
                    results["fact_check_results"].append(wiki_result)
            except Exception as e:
                logger.warning(f"Wikipedia check failed: {e}")
        
        # Calculate overall confidence and verdict
        if results["fact_check_results"]:
            results["confidence_score"] = self._calculate_confidence(results["fact_check_results"])
            results["verdict"] = self._determine_verdict(results["fact_check_results"])
        
        return results
    
    async def _check_google_factcheck(self, claim: str) -> Optional[Dict[str, Any]]:
        """Check claim against Google Fact Check API"""
        params = {
            "key": settings.GOOGLE_FACT_CHECK_API_KEY,
            "query": claim,
            "languageCode": "en"
        }
        
        async with self.session.get(self.google_factcheck_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                claims = data.get("claims", [])
                
                if claims:
                    claim_data = claims[0]  # Take first result
                    return {
                        "source": "google_factcheck",
                        "claim_text": claim_data.get("text", ""),
                        "claimant": claim_data.get("claimant", ""),
                        "rating": claim_data.get("claimReview", [{}])[0].get("textualRating", ""),
                        "url": claim_data.get("claimReview", [{}])[0].get("url", ""),
                        "publisher": claim_data.get("claimReview", [{}])[0].get("publisher", {}).get("name", "")
                    }
        
        return None
    
    async def _check_newsapi(self, claim: str) -> Optional[Dict[str, Any]]:
        """Check claim against NewsAPI"""
        params = {
            "apiKey": settings.NEWSAPI_KEY,
            "q": claim,
            "sortBy": "relevancy",
            "pageSize": 5,
            "language": "en"
        }
        
        async with self.session.get(self.newsapi_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                articles = data.get("articles", [])
                
                if articles:
                    return {
                        "source": "newsapi",
                        "articles_found": len(articles),
                        "top_articles": [
                            {
                                "title": article.get("title", ""),
                                "description": article.get("description", ""),
                                "url": article.get("url", ""),
                                "source": article.get("source", {}).get("name", ""),
                                "published_at": article.get("publishedAt", "")
                            }
                            for article in articles[:3]  # Top 3 articles
                        ]
                    }
        
        return None
    
    async def _check_wikipedia(self, claim: str) -> Optional[Dict[str, Any]]:
        """Check claim against Wikipedia"""
        # Extract key terms from claim for Wikipedia search
        search_terms = claim.split()[:3]  # Use first 3 words
        search_query = " ".join(search_terms)
        
        try:
            # First, search for the topic
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query.replace(' ', '_')}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "source": "wikipedia",
                        "title": data.get("title", ""),
                        "extract": data.get("extract", ""),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", "")
                    }
        except Exception as e:
            logger.debug(f"Wikipedia search failed for '{search_query}': {e}")
        
        return None
    
    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on fact-check results"""
        if not results:
            return 0.0
        
        # Simple confidence calculation based on number of sources
        base_confidence = len(results) * 0.3  # Each source adds 30%
        
        # Boost confidence if Google Fact Check found results
        for result in results:
            if result.get("source") == "google_factcheck" and result.get("rating"):
                base_confidence += 0.4
        
        return min(base_confidence, 1.0)  # Cap at 100%
    
    def _determine_verdict(self, results: List[Dict[str, Any]]) -> str:
        """Determine overall verdict from fact-check results"""
        # Check Google Fact Check rating first
        for result in results:
            if result.get("source") == "google_factcheck":
                rating = result.get("rating", "").lower()
                if any(word in rating for word in ["false", "fake", "incorrect", "misleading"]):
                    return "false"
                elif any(word in rating for word in ["true", "correct", "accurate"]):
                    return "true"
                elif any(word in rating for word in ["mixed", "partly", "partially"]):
                    return "mixed"
        
        # If multiple sources found, likely has some basis
        if len(results) >= 2:
            return "likely_true"
        elif len(results) == 1:
            return "needs_verification"
        
        return "unknown"

# Global AI service instance
ai_service = AIIntegrationService()
fact_checker = FactCheckingService()

# Convenience functions for common tasks
async def quick_bias_check(text: str) -> Dict[str, Any]:
    """Quick bias detection using Groq"""
    prompt = f"""Analyze the following text for bias. Look for political, cultural, religious, gender, racial, economic, regional, caste, or linguistic bias. Provide a JSON response with:
- bias_detected: boolean
- bias_types: list of detected bias types
- confidence_score: float (0-1)
- explanation: brief explanation

Text: {text}"""
    
    async with ai_service:
        return await ai_service.process_request(
            AITaskType.FAST_FILTER,
            prompt,
            max_tokens=500,
            temperature=0.0
        )

async def deep_misinformation_analysis(text: str) -> Dict[str, Any]:
    """Deep misinformation analysis using Gemini"""
    prompt = f"""Analyze the following text for misinformation. Provide detailed analysis including:
- misinformation_detected: boolean
- misinformation_type: type of misinformation (false_claim, misleading, clickbait, etc.)
- confidence_score: float (0-1)
- explanation: detailed explanation of why it's misinformation
- fact_check_suggestions: what should be verified
- educational_notes: how to spot similar misinformation

Text: {text}"""
    
    async with ai_service:
        return await ai_service.process_request(
            AITaskType.MISINFORMATION,
            prompt,
            max_tokens=1500,
            temperature=0.1
        )

async def generate_educational_content(topic: str, misinformation_type: str) -> Dict[str, Any]:
    """Generate educational content using Gemini"""
    prompt = f"""Create educational content about {misinformation_type} related to {topic}. Include:
- what_is_it: clear definition
- how_to_spot: warning signs and red flags
- why_it_spreads: psychological and social factors
- how_to_verify: step-by-step verification process
- examples: 2-3 examples (anonymized)
- resources: reliable sources for fact-checking

Make it accessible for general audience in both English and Hindi key points."""
    
    async with ai_service:
        return await ai_service.process_request(
            AITaskType.EDUCATION,
            prompt,
            max_tokens=2000,
            temperature=0.3
        )
