"""
🎯 Advanced Misinformation Detection Engine
AI-powered system for detecting fake news and misleading content
"""
import re
import asyncio
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import requests
from textstat import flesch_reading_ease, automated_readability_index
from urllib.parse import urlparse
import numpy as np

logger = logging.getLogger(__name__)

class MisinformationDetector:
    """Advanced misinformation detection with multiple AI models and fact-checking"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize classification pipelines
        try:
            # Fake news detection model
            self.fake_news_classifier = pipeline(
                "text-classification",
                model="hamzab/roberta-fake-news-classification",
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not load fake news classifier: {e}")
            self.fake_news_classifier = None
        
        try:
            # Bias detection model
            self.bias_classifier = pipeline(
                "text-classification",
                model="d4data/bias-detection-model",
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not load bias classifier: {e}")
            self.bias_classifier = None
        
        try:
            # Emotion analysis for manipulation detection
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not load emotion classifier: {e}")
            self.emotion_classifier = None
        
        # Misinformation indicators
        self.misinformation_patterns = {
            'sensational_language': {
                'patterns': [
                    re.compile(r'\b(SHOCKING|BREAKING|URGENT|EXCLUSIVE|LEAKED|SECRET)\b', re.IGNORECASE),
                    re.compile(r'\b(MUST READ|DON\'T MISS|INCREDIBLE|UNBELIEVABLE)\b', re.IGNORECASE),
                    re.compile(r'\b(THEY DON\'T WANT YOU TO KNOW|HIDDEN TRUTH|EXPOSED)\b', re.IGNORECASE),
                ],
                'weight': 15,
                'description': 'Sensational or clickbait language'
            },
            'emotional_manipulation': {
                'patterns': [
                    re.compile(r'\b(OUTRAGEOUS|DISGUSTING|TERRIFYING|HORRIFIC)\b', re.IGNORECASE),
                    re.compile(r'\b(YOU WON\'T BELIEVE|MIND-BLOWING|DEVASTATING)\b', re.IGNORECASE),
                ],
                'weight': 12,
                'description': 'Emotional manipulation tactics'
            },
            'conspiracy_indicators': {
                'patterns': [
                    re.compile(r'\b(COVER-UP|CONSPIRACY|DEEP STATE|AGENDA)\b', re.IGNORECASE),
                    re.compile(r'\b(THEY|THEM|ELITES|ESTABLISHMENT)\b(?=.*\b(CONTROL|HIDE|SUPPRESS)\b)', re.IGNORECASE),
                ],
                'weight': 20,
                'description': 'Conspiracy theory indicators'
            },
            'false_authority': {
                'patterns': [
                    re.compile(r'\b(EXPERTS SAY|STUDIES SHOW|RESEARCH PROVES)\b(?!.*\bcited\b)', re.IGNORECASE),
                    re.compile(r'\b(ACCORDING TO SOURCES|INSIDER REVEALS)\b', re.IGNORECASE),
                ],
                'weight': 10,
                'description': 'False authority claims'
            },
            'urgency_pressure': {
                'patterns': [
                    re.compile(r'\b(ACT NOW|LIMITED TIME|BEFORE IT\'S TOO LATE)\b', re.IGNORECASE),
                    re.compile(r'\b(SHARE IMMEDIATELY|SPREAD THE WORD|TELL EVERYONE)\b', re.IGNORECASE),
                ],
                'weight': 8,
                'description': 'Urgency and pressure tactics'
            }
        }
        
        # Credible source domains (whitelist)
        self.credible_domains = {
            'reuters.com', 'ap.org', 'bbc.com', 'cnn.com', 'nytimes.com',
            'washingtonpost.com', 'theguardian.com', 'npr.org', 'pbs.org',
            'nature.com', 'science.org', 'who.int', 'cdc.gov', 'nih.gov'
        }
        
        # Known unreliable domains (blacklist)
        self.unreliable_domains = {
            'infowars.com', 'naturalnews.com', 'beforeitsnews.com',
            'worldnewsdailyreport.com', 'theonion.com'  # Include satire sites
        }
        
        # Fact-checking APIs (mock endpoints for demonstration)
        self.fact_check_apis = {
            'google_fact_check': 'https://factchecktools.googleapis.com/v1alpha1/claims:search',
            'snopes': 'https://api.snopes.com/v1/fact-check',
            'politifact': 'https://api.politifact.com/v1/fact-check'
        }
    
    async def detect_misinformation(self, 
                                 text: str, 
                                 context: Optional[Dict] = None,
                                 urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive misinformation detection analysis
        """
        results = {
            'misinformation_indicators': [],
            'risk_score': 0,
            'credibility_score': 50,  # Start neutral
            'severity': 'low',
            'fact_check_results': [],
            'source_analysis': {},
            'content_analysis': {},
            'recommendations': [],
            'metadata': {
                'detection_timestamp': datetime.utcnow().isoformat(),
                'analysis_methods': [],
                'context': context or {}
            }
        }
        
        # Parallel analysis tasks
        analysis_tasks = [
            self._pattern_based_analysis(text, results),
            self._ai_model_analysis(text, results),
            self._linguistic_analysis(text, results),
            self._readability_analysis(text, results),
        ]
        
        # Add URL analysis if URLs provided
        if urls:
            analysis_tasks.append(self._source_credibility_analysis(urls, results))
            analysis_tasks.append(self._fact_check_analysis(text, urls, results))
        
        # Execute all analyses in parallel
        await asyncio.gather(*analysis_tasks, return_exceptions=True)
        
        # Calculate final scores
        self._calculate_misinformation_score(results)
        self._generate_recommendations(results)
        
        return results
    
    async def _pattern_based_analysis(self, text: str, results: Dict):
        """Pattern-based misinformation detection"""
        results['metadata']['analysis_methods'].append('pattern_based')
        
        pattern_score = 0
        detected_patterns = []
        
        for category, config in self.misinformation_patterns.items():
            category_matches = 0
            
            for pattern in config['patterns']:
                matches = pattern.findall(text)
                if matches:
                    category_matches += len(matches)
                    detected_patterns.extend(matches)
            
            if category_matches > 0:
                indicator = {
                    'type': 'pattern_match',
                    'category': category,
                    'matches': category_matches,
                    'weight': config['weight'],
                    'description': config['description'],
                    'severity': self._get_pattern_severity(config['weight']),
                    'examples': detected_patterns[-3:]  # Last 3 matches as examples
                }
                
                results['misinformation_indicators'].append(indicator)
                pattern_score += config['weight'] * min(category_matches, 3)  # Cap at 3 matches per category
        
        results['content_analysis']['pattern_score'] = min(pattern_score, 100)
    
    async def _ai_model_analysis(self, text: str, results: Dict):
        """AI model-based misinformation detection"""
        results['metadata']['analysis_methods'].append('ai_models')
        
        model_results = {}
        
        # Fake news classification
        if self.fake_news_classifier:
            try:
                fake_news_result = self.fake_news_classifier(text[:512])  # Truncate for model limits
                fake_score = max([score['score'] for score in fake_news_result[0] 
                                if score['label'].upper() in ['FAKE', 'FALSE']], default=0)
                
                model_results['fake_news_score'] = fake_score * 100
                
                if fake_score > self.confidence_threshold:
                    results['misinformation_indicators'].append({
                        'type': 'ai_classification',
                        'category': 'fake_news',
                        'confidence': fake_score,
                        'description': 'AI model detected potential fake news',
                        'severity': 'high' if fake_score > 0.9 else 'medium'
                    })
            except Exception as e:
                logger.error(f"Fake news classification error: {e}")
        
        # Bias detection
        if self.bias_classifier:
            try:
                bias_result = self.bias_classifier(text[:512])
                bias_score = max([score['score'] for score in bias_result[0] 
                                if 'bias' in score['label'].lower()], default=0)
                
                model_results['bias_score'] = bias_score * 100
                
                if bias_score > self.confidence_threshold:
                    results['misinformation_indicators'].append({
                        'type': 'ai_classification',
                        'category': 'bias_detection',
                        'confidence': bias_score,
                        'description': 'AI model detected potential bias',
                        'severity': 'medium'
                    })
            except Exception as e:
                logger.error(f"Bias classification error: {e}")
        
        # Emotion manipulation detection
        if self.emotion_classifier:
            try:
                emotion_result = self.emotion_classifier(text[:512])
                # Look for manipulative emotions (anger, fear, disgust)
                manipulative_emotions = ['anger', 'fear', 'disgust']
                manipulation_score = sum([score['score'] for score in emotion_result[0] 
                                        if score['label'].lower() in manipulative_emotions])
                
                model_results['emotion_manipulation_score'] = manipulation_score * 100
                
                if manipulation_score > 0.6:  # Lower threshold for emotion
                    results['misinformation_indicators'].append({
                        'type': 'ai_classification',
                        'category': 'emotion_manipulation',
                        'confidence': manipulation_score,
                        'description': 'Content uses manipulative emotional language',
                        'severity': 'medium'
                    })
            except Exception as e:
                logger.error(f"Emotion classification error: {e}")
        
        results['content_analysis']['ai_models'] = model_results
    
    async def _linguistic_analysis(self, text: str, results: Dict):
        """Linguistic analysis for misinformation indicators"""
        results['metadata']['analysis_methods'].append('linguistic')
        
        linguistic_indicators = {}
        
        # Basic text statistics
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Excessive punctuation (!!!, ???, etc.)
        excessive_punct = len(re.findall(r'[!?]{2,}', text))
        
        # ALL CAPS usage
        caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
        caps_ratio = caps_words / max(word_count, 1)
        
        # Spelling errors (simple heuristic)
        if self.nlp:
            doc = self.nlp(text)
            potential_errors = sum(1 for token in doc if token.is_alpha and not token.is_stop 
                                 and len(token.text) > 3 and token.text.islower())
        else:
            potential_errors = 0
        
        linguistic_indicators = {
            'word_count': word_count,
            'avg_sentence_length': avg_sentence_length,
            'excessive_punctuation': excessive_punct,
            'caps_ratio': caps_ratio,
            'potential_spelling_errors': potential_errors
        }
        
        # Flag suspicious linguistic patterns
        if excessive_punct > 5:
            results['misinformation_indicators'].append({
                'type': 'linguistic_pattern',
                'category': 'excessive_punctuation',
                'value': excessive_punct,
                'description': 'Excessive use of punctuation marks',
                'severity': 'low'
            })
        
        if caps_ratio > 0.1:  # More than 10% caps words
            results['misinformation_indicators'].append({
                'type': 'linguistic_pattern',
                'category': 'excessive_caps',
                'value': caps_ratio,
                'description': 'Excessive use of capital letters',
                'severity': 'low'
            })
        
        results['content_analysis']['linguistic'] = linguistic_indicators
    
    async def _readability_analysis(self, text: str, results: Dict):
        """Analyze text readability and complexity"""
        results['metadata']['analysis_methods'].append('readability')
        
        try:
            flesch_score = flesch_reading_ease(text)
            ari_score = automated_readability_index(text)
            
            readability_data = {
                'flesch_reading_ease': flesch_score,
                'automated_readability_index': ari_score,
                'reading_level': self._get_reading_level(flesch_score)
            }
            
            # Very low readability might indicate poor quality content
            if flesch_score < 30:  # Very difficult to read
                results['misinformation_indicators'].append({
                    'type': 'readability',
                    'category': 'poor_readability',
                    'value': flesch_score,
                    'description': 'Content has very poor readability',
                    'severity': 'low'
                })
            
            results['content_analysis']['readability'] = readability_data
            
        except Exception as e:
            logger.error(f"Readability analysis error: {e}")
    
    async def _source_credibility_analysis(self, urls: List[str], results: Dict):
        """Analyze source credibility based on domains"""
        results['metadata']['analysis_methods'].append('source_credibility')
        
        source_analysis = {
            'total_urls': len(urls),
            'credible_sources': 0,
            'unreliable_sources': 0,
            'unknown_sources': 0,
            'domain_analysis': []
        }
        
        for url in urls:
            try:
                domain = urlparse(url).netloc.lower()
                domain = domain.replace('www.', '')  # Remove www prefix
                
                domain_info = {
                    'domain': domain,
                    'url': url,
                    'credibility': 'unknown'
                }
                
                if domain in self.credible_domains:
                    domain_info['credibility'] = 'high'
                    source_analysis['credible_sources'] += 1
                elif domain in self.unreliable_domains:
                    domain_info['credibility'] = 'low'
                    source_analysis['unreliable_sources'] += 1
                    
                    results['misinformation_indicators'].append({
                        'type': 'source_credibility',
                        'category': 'unreliable_source',
                        'domain': domain,
                        'description': f'Content references unreliable source: {domain}',
                        'severity': 'high'
                    })
                else:
                    source_analysis['unknown_sources'] += 1
                
                source_analysis['domain_analysis'].append(domain_info)
                
            except Exception as e:
                logger.error(f"URL analysis error for {url}: {e}")
        
        # Calculate credibility score based on sources
        if source_analysis['total_urls'] > 0:
            credibility_ratio = source_analysis['credible_sources'] / source_analysis['total_urls']
            unreliable_ratio = source_analysis['unreliable_sources'] / source_analysis['total_urls']
            
            # Adjust credibility score
            results['credibility_score'] += (credibility_ratio * 30) - (unreliable_ratio * 40)
            results['credibility_score'] = max(0, min(100, results['credibility_score']))
        
        results['source_analysis'] = source_analysis
    
    async def _fact_check_analysis(self, text: str, urls: List[str], results: Dict):
        """Cross-reference with fact-checking databases"""
        results['metadata']['analysis_methods'].append('fact_checking')
        
        # This is a mock implementation - in production, you'd integrate with real APIs
        fact_check_results = []
        
        # Generate content hash for fact-check lookup
        content_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Mock fact-check result (replace with real API calls)
        mock_fact_check = {
            'source': 'mock_fact_checker',
            'claim_reviewed': text[:100] + '...' if len(text) > 100 else text,
            'rating': 'unverified',  # Could be: true, false, mixed, unverified
            'confidence': 0.0,
            'review_url': None,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        fact_check_results.append(mock_fact_check)
        
        # In a real implementation, you would:
        # 1. Extract key claims from the text
        # 2. Query multiple fact-checking APIs
        # 3. Analyze the results and confidence scores
        # 4. Flag content based on fact-check results
        
        results['fact_check_results'] = fact_check_results
    
    def _calculate_misinformation_score(self, results: Dict):
        """Calculate overall misinformation risk score"""
        base_score = 0
        
        # Pattern-based score
        pattern_score = results['content_analysis'].get('pattern_score', 0)
        base_score += pattern_score * 0.3
        
        # AI model scores
        ai_models = results['content_analysis'].get('ai_models', {})
        fake_news_score = ai_models.get('fake_news_score', 0)
        bias_score = ai_models.get('bias_score', 0)
        emotion_score = ai_models.get('emotion_manipulation_score', 0)
        
        base_score += fake_news_score * 0.4
        base_score += bias_score * 0.2
        base_score += emotion_score * 0.1
        
        # Source credibility impact
        credibility_penalty = max(0, 50 - results['credibility_score']) * 0.5
        base_score += credibility_penalty
        
        # Normalize score
        results['risk_score'] = min(100, max(0, base_score))
        
        # Determine severity
        if results['risk_score'] >= 80:
            results['severity'] = 'critical'
        elif results['risk_score'] >= 60:
            results['severity'] = 'high'
        elif results['risk_score'] >= 40:
            results['severity'] = 'medium'
        elif results['risk_score'] >= 20:
            results['severity'] = 'low'
        else:
            results['severity'] = 'minimal'
    
    def _generate_recommendations(self, results: Dict):
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        risk_score = results['risk_score']
        
        if risk_score >= 80:
            recommendations.extend([
                "CRITICAL: Block or heavily flag this content",
                "Require manual review before publication",
                "Add prominent misinformation warning",
                "Limit content distribution and sharing"
            ])
        elif risk_score >= 60:
            recommendations.extend([
                "Add fact-check warning labels",
                "Reduce content visibility in feeds",
                "Prompt users to verify information",
                "Link to authoritative sources"
            ])
        elif risk_score >= 40:
            recommendations.extend([
                "Monitor engagement patterns",
                "Suggest related fact-checked content",
                "Add context information"
            ])
        elif risk_score >= 20:
            recommendations.append("Log for pattern analysis")
        
        # Specific recommendations based on detected indicators
        for indicator in results['misinformation_indicators']:
            if indicator['category'] == 'unreliable_source':
                recommendations.append(f"Verify claims independently of {indicator['domain']}")
            elif indicator['category'] == 'conspiracy_indicators':
                recommendations.append("Cross-reference with multiple credible sources")
            elif indicator['category'] == 'emotional_manipulation':
                recommendations.append("Encourage critical thinking and fact verification")
        
        results['recommendations'] = list(set(recommendations))  # Remove duplicates
    
    def _get_pattern_severity(self, weight: int) -> str:
        """Convert pattern weight to severity level"""
        if weight >= 20:
            return 'high'
        elif weight >= 10:
            return 'medium'
        else:
            return 'low'
    
    def _get_reading_level(self, flesch_score: float) -> str:
        """Convert Flesch score to reading level"""
        if flesch_score >= 90:
            return "Very Easy"
        elif flesch_score >= 80:
            return "Easy"
        elif flesch_score >= 70:
            return "Fairly Easy"
        elif flesch_score >= 60:
            return "Standard"
        elif flesch_score >= 50:
            return "Fairly Difficult"
        elif flesch_score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def get_detection_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate comprehensive detection summary"""
        return {
            'overall_assessment': {
                'risk_score': results['risk_score'],
                'credibility_score': results['credibility_score'],
                'severity': results['severity'],
                'is_likely_misinformation': results['risk_score'] >= 60
            },
            'detection_summary': {
                'total_indicators': len(results['misinformation_indicators']),
                'by_category': self._count_by_category(results['misinformation_indicators']),
                'by_severity': self._count_by_severity(results['misinformation_indicators'])
            },
            'source_summary': results.get('source_analysis', {}),
            'recommendations_count': len(results['recommendations']),
            'analysis_methods': results['metadata']['analysis_methods']
        }
    
    def _count_by_category(self, indicators: List[Dict]) -> Dict[str, int]:
        """Count indicators by category"""
        counts = {}
        for indicator in indicators:
            category = indicator['category']
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _count_by_severity(self, indicators: List[Dict]) -> Dict[str, int]:
        """Count indicators by severity"""
        counts = {}
        for indicator in indicators:
            severity = indicator.get('severity', 'unknown')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
