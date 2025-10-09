"""
🔍 Comprehensive Fact-Checking Service
Integrates Google Fact Check API, NewsAPI, and Wikipedia for misinformation detection
"""

import logging
import asyncio
import aiohttp
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

from app.core.config import settings
from app.core.database import get_database

logger = logging.getLogger(__name__)

class FactCheckStatus(Enum):
    """Fact-check verification status"""
    TRUE = "true"
    FALSE = "false"
    MIXED = "mixed"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    SATIRE = "satire"

class SourceReliability(Enum):
    """Source reliability rating"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

@dataclass
class FactCheckResult:
    """Fact-check result data structure"""
    claim: str
    status: FactCheckStatus
    confidence: float
    sources: List[Dict[str, Any]]
    explanation: str
    evidence: List[str]
    contradictions: List[str]
    timestamp: datetime

class ComprehensiveFactChecker:
    """
    🔍 Comprehensive Fact-Checking Engine
    
    Combines multiple fact-checking sources for robust misinformation detection
    """
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_FACT_CHECK_API_KEY
        self.newsapi_key = settings.NEWSAPI_KEY
        self.session = None
        self.cache = {}  # In production, use Redis
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.FACT_CHECK_TIMEOUT_SECONDS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def comprehensive_fact_check(self, claim: str, context: Optional[str] = None) -> FactCheckResult:
        """
        Perform comprehensive fact-checking using multiple sources
        
        Args:
            claim: The claim to fact-check
            context: Additional context for the claim
            
        Returns:
            FactCheckResult with verification status and evidence
        """
        try:
            # Check cache first
            cache_key = f"fact_check:{hash(claim)}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if datetime.utcnow() - cached_result["timestamp"] < timedelta(hours=24):
                    return cached_result["result"]
            
            # Run fact-checking from multiple sources in parallel
            tasks = []
            
            if settings.GOOGLE_FACT_CHECK_ENABLED and self.google_api_key:
                tasks.append(self._google_fact_check(claim))
            
            if settings.NEWSAPI_ENABLED and self.newsapi_key:
                tasks.append(self._newsapi_verification(claim))
            
            if settings.WIKIPEDIA_ENABLED:
                tasks.append(self._wikipedia_verification(claim))
            
            # Execute all fact-checking tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process and combine results
            google_result = results[0] if len(results) > 0 and not isinstance(results[0], Exception) else None
            news_result = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else None
            wiki_result = results[2] if len(results) > 2 and not isinstance(results[2], Exception) else None
            
            # Combine results into comprehensive assessment
            final_result = self._combine_fact_check_results(
                claim, google_result, news_result, wiki_result, context
            )
            
            # Cache the result
            self.cache[cache_key] = {
                "result": final_result,
                "timestamp": datetime.utcnow()
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Comprehensive fact-check failed: {e}")
            return FactCheckResult(
                claim=claim,
                status=FactCheckStatus.UNVERIFIED,
                confidence=0.0,
                sources=[],
                explanation=f"Fact-checking failed due to technical error: {str(e)}",
                evidence=[],
                contradictions=[],
                timestamp=datetime.utcnow()
            )
    
    async def _google_fact_check(self, claim: str) -> Optional[Dict[str, Any]]:
        """Fact-check using Google Fact Check Tools API"""
        try:
            if not self.google_api_key:
                return None
            
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                "key": self.google_api_key,
                "query": claim,
                "languageCode": "en",
                "maxAgeDays": 30,
                "pageSize": 10
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "claims" in data and data["claims"]:
                        # Process Google Fact Check results
                        claims = data["claims"]
                        
                        # Find the most relevant claim
                        best_match = self._find_best_claim_match(claim, claims)
                        
                        if best_match:
                            return {
                                "source": "Google Fact Check",
                                "reliability": SourceReliability.HIGH,
                                "claim_reviewed": best_match.get("text", ""),
                                "rating": self._parse_google_rating(best_match),
                                "publisher": best_match.get("claimant", "Unknown"),
                                "review_date": best_match.get("claimDate", ""),
                                "review_url": self._extract_review_url(best_match),
                                "raw_data": best_match
                            }
                
                return None
                
        except Exception as e:
            logger.error(f"Google Fact Check API error: {e}")
            return None
    
    async def _newsapi_verification(self, claim: str) -> Optional[Dict[str, Any]]:
        """Verify claim using NewsAPI for recent news coverage"""
        try:
            if not self.newsapi_key:
                return None
            
            # Extract key terms from claim for search
            search_terms = self._extract_search_terms(claim)
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "apiKey": self.newsapi_key,
                "q": " AND ".join(search_terms[:3]),  # Use top 3 terms
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": 20,
                "from": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "articles" in data and data["articles"]:
                        articles = data["articles"]
                        
                        # Analyze articles for claim verification
                        supporting_articles = []
                        contradicting_articles = []
                        
                        for article in articles[:10]:  # Analyze top 10 articles
                            relevance_score = self._calculate_article_relevance(claim, article)
                            
                            if relevance_score > 0.6:
                                article_analysis = {
                                    "title": article.get("title", ""),
                                    "source": article.get("source", {}).get("name", "Unknown"),
                                    "url": article.get("url", ""),
                                    "published_at": article.get("publishedAt", ""),
                                    "relevance_score": relevance_score,
                                    "description": article.get("description", "")
                                }
                                
                                # Simple sentiment analysis to determine support/contradiction
                                if self._article_supports_claim(claim, article):
                                    supporting_articles.append(article_analysis)
                                else:
                                    contradicting_articles.append(article_analysis)
                        
                        return {
                            "source": "NewsAPI",
                            "reliability": SourceReliability.MEDIUM,
                            "supporting_articles": supporting_articles,
                            "contradicting_articles": contradicting_articles,
                            "total_articles_analyzed": len(articles),
                            "search_terms": search_terms
                        }
                
                return None
                
        except Exception as e:
            logger.error(f"NewsAPI verification error: {e}")
            return None
    
    async def _wikipedia_verification(self, claim: str) -> Optional[Dict[str, Any]]:
        """Verify claim against Wikipedia knowledge base"""
        try:
            # Extract entities and topics from claim
            entities = self._extract_entities(claim)
            
            if not entities:
                return None
            
            wikipedia_results = []
            
            for entity in entities[:3]:  # Check top 3 entities
                # Search Wikipedia
                search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + entity.replace(" ", "_")
                
                try:
                    async with self.session.get(search_url) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if "extract" in data:
                                wikipedia_results.append({
                                    "entity": entity,
                                    "title": data.get("title", ""),
                                    "extract": data.get("extract", ""),
                                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                                    "relevance": self._calculate_wikipedia_relevance(claim, data.get("extract", ""))
                                })
                
                except Exception as e:
                    logger.warning(f"Wikipedia lookup failed for {entity}: {e}")
                    continue
            
            if wikipedia_results:
                return {
                    "source": "Wikipedia",
                    "reliability": SourceReliability.HIGH,
                    "entities_found": len(wikipedia_results),
                    "results": wikipedia_results,
                    "entities_searched": entities
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Wikipedia verification error: {e}")
            return None
    
    def _combine_fact_check_results(self, claim: str, google_result: Optional[Dict], 
                                  news_result: Optional[Dict], wiki_result: Optional[Dict],
                                  context: Optional[str]) -> FactCheckResult:
        """Combine results from multiple fact-checking sources"""
        
        sources = []
        evidence = []
        contradictions = []
        confidence_scores = []
        
        # Process Google Fact Check results
        if google_result:
            sources.append(google_result)
            
            rating = google_result.get("rating", {})
            if rating.get("status") == "FALSE":
                contradictions.append(f"Google Fact Check: {rating.get('explanation', 'Claim rated as false')}")
                confidence_scores.append(0.9)
            elif rating.get("status") == "TRUE":
                evidence.append(f"Google Fact Check: {rating.get('explanation', 'Claim verified as true')}")
                confidence_scores.append(0.9)
            else:
                confidence_scores.append(0.5)
        
        # Process NewsAPI results
        if news_result:
            sources.append(news_result)
            
            supporting = news_result.get("supporting_articles", [])
            contradicting = news_result.get("contradicting_articles", [])
            
            if supporting:
                evidence.extend([f"News coverage supports claim: {article['title']}" for article in supporting[:3]])
                confidence_scores.append(0.7)
            
            if contradicting:
                contradictions.extend([f"News coverage contradicts claim: {article['title']}" for article in contradicting[:3]])
                confidence_scores.append(0.7)
            
            if not supporting and not contradicting:
                confidence_scores.append(0.3)
        
        # Process Wikipedia results
        if wiki_result:
            sources.append(wiki_result)
            
            for result in wiki_result.get("results", []):
                if result["relevance"] > 0.7:
                    evidence.append(f"Wikipedia reference: {result['title']} - {result['extract'][:200]}...")
                    confidence_scores.append(0.6)
        
        # Determine overall status
        status = self._determine_overall_status(evidence, contradictions)
        
        # Calculate confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Generate explanation
        explanation = self._generate_explanation(claim, status, evidence, contradictions, sources)
        
        return FactCheckResult(
            claim=claim,
            status=status,
            confidence=min(overall_confidence, 1.0),
            sources=sources,
            explanation=explanation,
            evidence=evidence,
            contradictions=contradictions,
            timestamp=datetime.utcnow()
        )
    
    def _find_best_claim_match(self, original_claim: str, claims: List[Dict]) -> Optional[Dict]:
        """Find the best matching claim from Google Fact Check results"""
        best_match = None
        best_score = 0.0
        
        for claim_data in claims:
            claim_text = claim_data.get("text", "")
            similarity = self._calculate_text_similarity(original_claim, claim_text)
            
            if similarity > best_score:
                best_score = similarity
                best_match = claim_data
        
        return best_match if best_score > 0.5 else None
    
    def _parse_google_rating(self, claim_data: Dict) -> Dict[str, Any]:
        """Parse Google Fact Check rating"""
        claim_review = claim_data.get("claimReview", [])
        
        if claim_review:
            review = claim_review[0]
            rating = review.get("reviewRating", {})
            
            return {
                "status": self._normalize_rating(rating.get("ratingValue", "")),
                "explanation": rating.get("ratingExplanation", ""),
                "reviewer": review.get("publisher", {}).get("name", "Unknown"),
                "review_date": review.get("reviewDate", ""),
                "raw_rating": rating.get("ratingValue", "")
            }
        
        return {"status": "UNVERIFIED", "explanation": "No rating available"}
    
    def _extract_search_terms(self, text: str) -> List[str]:
        """Extract key search terms from text"""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has"
        }
        
        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text.lower())
        
        # Filter out stop words and return unique terms
        terms = list(set([word for word in words if word not in stop_words]))
        
        # Sort by length (longer terms are often more specific)
        return sorted(terms, key=len, reverse=True)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text for Wikipedia lookup"""
        # Simple entity extraction - look for capitalized words/phrases
        entities = []
        
        # Find capitalized phrases (potential proper nouns)
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend(capitalized_phrases)
        
        # Find quoted terms
        quoted_terms = re.findall(r'"([^"]+)"', text)
        entities.extend(quoted_terms)
        
        # Remove duplicates and filter
        unique_entities = list(set(entities))
        
        # Filter out common words that might be capitalized
        common_words = {"The", "This", "That", "There", "Here", "When", "Where", "What", "Who", "Why", "How"}
        filtered_entities = [entity for entity in unique_entities if entity not in common_words]
        
        return filtered_entities[:5]  # Return top 5 entities
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_article_relevance(self, claim: str, article: Dict) -> float:
        """Calculate how relevant an article is to the claim"""
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        claim_lower = claim.lower()
        
        # Simple relevance scoring
        title_score = self._calculate_text_similarity(claim_lower, title) * 0.6
        desc_score = self._calculate_text_similarity(claim_lower, description) * 0.4
        
        return title_score + desc_score
    
    def _article_supports_claim(self, claim: str, article: Dict) -> bool:
        """Determine if article supports or contradicts the claim (simplified)"""
        # This is a simplified implementation
        # In production, you'd use more sophisticated NLP
        
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        
        negative_indicators = ["false", "fake", "debunked", "myth", "untrue", "incorrect", "wrong"]
        positive_indicators = ["confirmed", "verified", "true", "accurate", "correct", "factual"]
        
        text_to_analyze = f"{title} {description}"
        
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_to_analyze)
        positive_count = sum(1 for indicator in positive_indicators if indicator in text_to_analyze)
        
        return positive_count > negative_count
    
    def _calculate_wikipedia_relevance(self, claim: str, extract: str) -> float:
        """Calculate relevance of Wikipedia extract to claim"""
        return self._calculate_text_similarity(claim.lower(), extract.lower())
    
    def _normalize_rating(self, rating_value: str) -> str:
        """Normalize different rating formats to standard status"""
        rating_lower = rating_value.lower()
        
        if any(term in rating_lower for term in ["false", "fake", "incorrect", "wrong"]):
            return "FALSE"
        elif any(term in rating_lower for term in ["true", "correct", "accurate", "verified"]):
            return "TRUE"
        elif any(term in rating_lower for term in ["mixed", "partly", "partially"]):
            return "MIXED"
        elif any(term in rating_lower for term in ["satire", "humor", "joke"]):
            return "SATIRE"
        else:
            return "UNVERIFIED"
    
    def _determine_overall_status(self, evidence: List[str], contradictions: List[str]) -> FactCheckStatus:
        """Determine overall fact-check status based on evidence"""
        if not evidence and not contradictions:
            return FactCheckStatus.UNVERIFIED
        
        evidence_count = len(evidence)
        contradiction_count = len(contradictions)
        
        if contradiction_count > evidence_count * 1.5:
            return FactCheckStatus.FALSE
        elif evidence_count > contradiction_count * 1.5:
            return FactCheckStatus.TRUE
        elif evidence_count > 0 and contradiction_count > 0:
            return FactCheckStatus.MIXED
        else:
            return FactCheckStatus.DISPUTED
    
    def _generate_explanation(self, claim: str, status: FactCheckStatus, 
                            evidence: List[str], contradictions: List[str], 
                            sources: List[Dict]) -> str:
        """Generate human-readable explanation of fact-check results"""
        
        explanation_parts = [f"Fact-check analysis for: '{claim}'"]
        
        # Status explanation
        status_explanations = {
            FactCheckStatus.TRUE: "This claim appears to be supported by available evidence.",
            FactCheckStatus.FALSE: "This claim appears to be contradicted by available evidence.",
            FactCheckStatus.MIXED: "This claim has both supporting and contradicting evidence.",
            FactCheckStatus.UNVERIFIED: "This claim could not be verified with available sources.",
            FactCheckStatus.DISPUTED: "This claim is disputed with conflicting information.",
            FactCheckStatus.SATIRE: "This claim appears to be satirical or humorous content."
        }
        
        explanation_parts.append(status_explanations.get(status, "Status unclear."))
        
        # Sources used
        source_names = [source.get("source", "Unknown") for source in sources]
        if source_names:
            explanation_parts.append(f"Sources consulted: {', '.join(source_names)}")
        
        # Evidence summary
        if evidence:
            explanation_parts.append(f"Supporting evidence found: {len(evidence)} items")
        
        if contradictions:
            explanation_parts.append(f"Contradicting evidence found: {len(contradictions)} items")
        
        return " ".join(explanation_parts)
    
    def _extract_review_url(self, claim_data: Dict) -> str:
        """Extract review URL from Google Fact Check data"""
        claim_review = claim_data.get("claimReview", [])
        if claim_review:
            return claim_review[0].get("url", "")
        return ""

class FactCheckingService:
    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = db
        self.sources = {
            "google": settings.GOOGLE_FACT_CHECK_ENABLED,
            "newsapi": settings.NEWSAPI_ENABLED,
            "wikipedia": settings.WIKIPEDIA_ENABLED
        }

    async def verify(self, claim: str) -> Dict[str, Any]:
        """Verify a claim using configured fact checking sources"""
        try:
            # Track verification request
            await self._track_request(claim)
            
            results = []
            
            # Check each enabled source
            for source, enabled in self.sources.items():
                if enabled:
                    result = await self._check_source(source, claim)
                    if result:
                        results.append(result)
            
            # Aggregate results
            verification = self._aggregate_results(results)
            
            return {
                "claim": claim,
                "verification_status": verification["status"],
                "confidence_score": verification["confidence"],
                "sources": len(results),
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fact checking failed: {str(e)}")
            return {
                "claim": claim,
                "verification_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _check_source(self, source: str, claim: str) -> Optional[Dict[str, Any]]:
        """Check a claim against a specific source"""
        try:
            if source == "google":
                return await self._check_google_fact_check(claim)
            elif source == "newsapi":
                return await self._check_newsapi(claim)
            elif source == "wikipedia":
                return await self._check_wikipedia(claim)
            return None
        except Exception as e:
            logger.error(f"Source {source} check failed: {str(e)}")
            return None

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple sources"""
        if not results:
            return {"status": "unknown", "confidence": 0.0}
        
        # Count verdicts
        verdicts = {"true": 0, "false": 0, "mixed": 0, "unknown": 0}
        total_confidence = 0.0
        
        for result in results:
            verdicts[result.get("status", "unknown")] += 1
            total_confidence += result.get("confidence", 0.0)
        
        # Determine overall status
        if verdicts["true"] > verdicts["false"]:
            status = "true"
        elif verdicts["false"] > verdicts["true"]:
            status = "false"
        elif verdicts["mixed"] > 0:
            status = "mixed"
        else:
            status = "unknown"
        
        # Calculate confidence
        confidence = total_confidence / len(results) if results else 0.0
        
        return {
            "status": status,
            "confidence": round(confidence, 2)
        }

    async def _track_request(self, claim: str) -> None:
        """Track fact checking request for analytics"""
        try:
            await self.db.fact_check_requests.insert_one({
                "claim": claim,
                "timestamp": datetime.utcnow(),
                "sources": list(self.sources.keys())
            })
        except Exception as e:
            logger.error(f"Failed to track fact check request: {str(e)}")

    async def _check_google_fact_check(self, claim: str) -> Optional[Dict[str, Any]]:
        """Implement Google Fact Check API integration"""
        # TODO: Implement Google Fact Check API
        return None

    async def _check_newsapi(self, claim: str) -> Optional[Dict[str, Any]]:
        """Implement NewsAPI integration"""
        # TODO: Implement NewsAPI integration
        return None

    async def _check_wikipedia(self, claim: str) -> Optional[Dict[str, Any]]:
        """Implement Wikipedia verification"""
        # TODO: Implement Wikipedia integration
        return None

# Global fact checker instance
fact_checker = ComprehensiveFactChecker()

# Convenience function
async def fact_check_claim(claim: str, context: Optional[str] = None) -> FactCheckResult:
    """Quick fact-checking function"""
    async with fact_checker as checker:
        return await checker.comprehensive_fact_check(claim, context)
