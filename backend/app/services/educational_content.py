"""
🎓 Educational Content Generation Service
Generates educational content for misinformation detection and digital literacy
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from app.core.config import settings
from app.core.database import get_database_operations

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of educational content"""
    EXPLANATION = "explanation"
    FACT_CHECK_GUIDE = "fact_check_guide"
    BIAS_AWARENESS = "bias_awareness"
    DIGITAL_LITERACY = "digital_literacy"
    MISINFORMATION_EXAMPLE = "misinformation_example"
    CRITICAL_THINKING = "critical_thinking"

class DifficultyLevel(Enum):
    """Content difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class EducationalContent:
    """Educational content structure"""
    title: str
    content: str
    content_type: ContentType
    difficulty_level: DifficultyLevel
    key_points: List[str]
    examples: List[Dict[str, Any]]
    interactive_elements: List[Dict[str, Any]]
    sources: List[str]
    metadata: Dict[str, Any]

class EducationalContentGenerator:
    """
    🎓 Educational Content Generation Service
    
    Generates comprehensive educational content for:
    - Misinformation detection techniques
    - Digital literacy skills
    - Critical thinking development
    - Bias awareness training
    - Fact-checking methodologies
    """
    
    def __init__(self):
        self.content_templates = self._load_content_templates()
        self.misinformation_examples = self._load_misinformation_examples()
        self.fact_checking_techniques = self._load_fact_checking_techniques()
        
    def _load_content_templates(self) -> Dict[str, Dict]:
        """Load educational content templates"""
        return {
            ContentType.EXPLANATION.value: {
                "structure": ["introduction", "main_content", "key_takeaways", "practice_exercises"],
                "tone": "educational",
                "length": "medium"
            },
            ContentType.FACT_CHECK_GUIDE.value: {
                "structure": ["overview", "step_by_step", "tools_resources", "common_pitfalls"],
                "tone": "instructional",
                "length": "detailed"
            },
            ContentType.BIAS_AWARENESS.value: {
                "structure": ["bias_definition", "examples", "recognition_techniques", "mitigation_strategies"],
                "tone": "awareness",
                "length": "comprehensive"
            },
            ContentType.DIGITAL_LITERACY.value: {
                "structure": ["fundamentals", "practical_skills", "safety_measures", "best_practices"],
                "tone": "practical",
                "length": "extensive"
            }
        }
    
    def _load_misinformation_examples(self) -> List[Dict]:
        """Load curated misinformation examples for educational purposes"""
        return [
            {
                "category": "health_misinformation",
                "example": "Miracle cure claims without scientific evidence",
                "red_flags": ["Absolute claims", "No peer review", "Anecdotal evidence only"],
                "fact_check_approach": "Check medical journals, consult healthcare professionals"
            },
            {
                "category": "political_misinformation",
                "example": "Out-of-context quotes or statistics",
                "red_flags": ["Missing context", "Selective data", "Emotional language"],
                "fact_check_approach": "Verify original source, check full context, cross-reference"
            },
            {
                "category": "technology_misinformation",
                "example": "False claims about AI capabilities or risks",
                "red_flags": ["Sensational headlines", "Lack of technical detail", "Fear-mongering"],
                "fact_check_approach": "Consult technical experts, check peer-reviewed research"
            },
            {
                "category": "social_misinformation",
                "example": "Fabricated social media posts or viral content",
                "red_flags": ["Unverified sources", "Emotional manipulation", "Rapid spread"],
                "fact_check_approach": "Reverse image search, check original posting date, verify accounts"
            }
        ]
    
    def _load_fact_checking_techniques(self) -> List[Dict]:
        """Load fact-checking methodologies and techniques"""
        return [
            {
                "technique": "Source Verification",
                "description": "Verify the credibility and expertise of information sources",
                "steps": [
                    "Check author credentials and expertise",
                    "Verify publication reputation",
                    "Look for peer review or editorial oversight",
                    "Check for conflicts of interest"
                ],
                "tools": ["Author lookup databases", "Publication rankings", "Conflict of interest disclosures"]
            },
            {
                "technique": "Cross-Referencing",
                "description": "Compare information across multiple reliable sources",
                "steps": [
                    "Find at least 2-3 independent sources",
                    "Compare key facts and figures",
                    "Note any discrepancies",
                    "Prioritize authoritative sources"
                ],
                "tools": ["News aggregators", "Academic databases", "Government sources"]
            },
            {
                "technique": "Evidence Evaluation",
                "description": "Assess the quality and reliability of presented evidence",
                "steps": [
                    "Distinguish between correlation and causation",
                    "Check sample sizes and methodology",
                    "Look for peer review",
                    "Assess statistical significance"
                ],
                "tools": ["Research methodology guides", "Statistical analysis tools", "Peer review databases"]
            },
            {
                "technique": "Bias Detection",
                "description": "Identify potential biases in information presentation",
                "steps": [
                    "Check for loaded language",
                    "Look for missing perspectives",
                    "Assess cherry-picking of data",
                    "Consider source motivations"
                ],
                "tools": ["Bias detection frameworks", "Multiple perspective sources", "Fact-checking sites"]
            }
        ]
    
    async def generate_misinformation_explanation(self, 
                                                topic: str, 
                                                detected_issues: List[str],
                                                difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> EducationalContent:
        """
        Generate educational explanation about detected misinformation
        
        Args:
            topic: The topic or claim being explained
            detected_issues: List of detected misinformation issues
            difficulty_level: Target audience difficulty level
            
        Returns:
            EducationalContent with comprehensive explanation
        """
        
        logger.info(f"🎓 Generating misinformation explanation for topic: {topic}")
        
        # Generate title
        title = f"Understanding Misinformation: {topic}"
        
        # Build content sections
        content_sections = []
        
        # Introduction
        intro = self._generate_introduction(topic, detected_issues, difficulty_level)
        content_sections.append(f"## Introduction\n{intro}")
        
        # Main explanation
        main_content = self._generate_main_explanation(topic, detected_issues, difficulty_level)
        content_sections.append(f"## What Makes This Misinformation?\n{main_content}")
        
        # Red flags section
        red_flags = self._generate_red_flags_section(detected_issues)
        content_sections.append(f"## Red Flags to Watch For\n{red_flags}")
        
        # Fact-checking guidance
        fact_check_guide = self._generate_fact_checking_guidance(topic, difficulty_level)
        content_sections.append(f"## How to Fact-Check This Type of Information\n{fact_check_guide}")
        
        # Key takeaways
        key_points = self._generate_key_points(detected_issues)
        takeaways = "\n".join([f"• {point}" for point in key_points])
        content_sections.append(f"## Key Takeaways\n{takeaways}")
        
        # Combine all sections
        full_content = "\n\n".join(content_sections)
        
        # Generate examples
        examples = self._generate_relevant_examples(topic, detected_issues)
        
        # Generate interactive elements
        interactive_elements = self._generate_interactive_elements(topic, detected_issues, difficulty_level)
        
        # Compile sources
        sources = self._compile_educational_sources(topic)
        
        # Create metadata
        metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "topic": topic,
            "detected_issues": detected_issues,
            "word_count": len(full_content.split()),
            "estimated_reading_time": max(1, len(full_content.split()) // 200)  # ~200 words per minute
        }
        
        return EducationalContent(
            title=title,
            content=full_content,
            content_type=ContentType.EXPLANATION,
            difficulty_level=difficulty_level,
            key_points=key_points,
            examples=examples,
            interactive_elements=interactive_elements,
            sources=sources,
            metadata=metadata
        )
    
    async def generate_fact_checking_guide(self, 
                                         content_category: str,
                                         difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> EducationalContent:
        """
        Generate comprehensive fact-checking guide for specific content category
        
        Args:
            content_category: Category of content (health, politics, technology, etc.)
            difficulty_level: Target audience difficulty level
            
        Returns:
            EducationalContent with fact-checking methodology
        """
        
        logger.info(f"🎓 Generating fact-checking guide for category: {content_category}")
        
        title = f"Fact-Checking Guide: {content_category.title()} Information"
        
        # Build comprehensive guide
        content_sections = []
        
        # Overview
        overview = self._generate_category_overview(content_category)
        content_sections.append(f"## Overview\n{overview}")
        
        # Step-by-step process
        steps = self._generate_fact_checking_steps(content_category, difficulty_level)
        content_sections.append(f"## Step-by-Step Fact-Checking Process\n{steps}")
        
        # Tools and resources
        tools = self._generate_fact_checking_tools(content_category)
        content_sections.append(f"## Essential Tools and Resources\n{tools}")
        
        # Common pitfalls
        pitfalls = self._generate_common_pitfalls(content_category)
        content_sections.append(f"## Common Pitfalls to Avoid\n{pitfalls}")
        
        # Practice exercises
        exercises = self._generate_practice_exercises(content_category, difficulty_level)
        content_sections.append(f"## Practice Exercises\n{exercises}")
        
        full_content = "\n\n".join(content_sections)
        
        # Generate supporting elements
        key_points = self._extract_key_points_from_guide(content_category)
        examples = self._get_category_examples(content_category)
        interactive_elements = self._generate_guide_interactive_elements(content_category, difficulty_level)
        sources = self._compile_fact_checking_sources(content_category)
        
        metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "category": content_category,
            "guide_type": "fact_checking",
            "word_count": len(full_content.split()),
            "estimated_completion_time": max(10, len(full_content.split()) // 100)  # ~100 words per minute for learning
        }
        
        return EducationalContent(
            title=title,
            content=full_content,
            content_type=ContentType.FACT_CHECK_GUIDE,
            difficulty_level=difficulty_level,
            key_points=key_points,
            examples=examples,
            interactive_elements=interactive_elements,
            sources=sources,
            metadata=metadata
        )
    
    async def generate_bias_awareness_content(self, 
                                            bias_types: List[str],
                                            cultural_context: str = "indian",
                                            difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE) -> EducationalContent:
        """
        Generate bias awareness and mitigation content
        
        Args:
            bias_types: Types of biases to address
            cultural_context: Cultural context for examples
            difficulty_level: Target audience difficulty level
            
        Returns:
            EducationalContent focused on bias awareness
        """
        
        logger.info(f"🎓 Generating bias awareness content for types: {bias_types}")
        
        title = "Understanding and Recognizing Bias in Information"
        
        content_sections = []
        
        # Introduction to bias
        intro = self._generate_bias_introduction(bias_types, cultural_context)
        content_sections.append(f"## Understanding Bias\n{intro}")
        
        # Specific bias types
        for bias_type in bias_types:
            bias_section = self._generate_bias_type_section(bias_type, cultural_context, difficulty_level)
            content_sections.append(f"## {bias_type.title()} Bias\n{bias_section}")
        
        # Recognition techniques
        recognition = self._generate_bias_recognition_techniques(bias_types)
        content_sections.append(f"## How to Recognize Bias\n{recognition}")
        
        # Mitigation strategies
        mitigation = self._generate_bias_mitigation_strategies(bias_types, cultural_context)
        content_sections.append(f"## Strategies to Mitigate Bias\n{mitigation}")
        
        full_content = "\n\n".join(content_sections)
        
        # Supporting elements
        key_points = self._generate_bias_key_points(bias_types)
        examples = self._generate_bias_examples(bias_types, cultural_context)
        interactive_elements = self._generate_bias_interactive_elements(bias_types, difficulty_level)
        sources = self._compile_bias_awareness_sources()
        
        metadata = {
            "generated_at": datetime.utcnow().isoformat(),
            "bias_types": bias_types,
            "cultural_context": cultural_context,
            "word_count": len(full_content.split()),
            "estimated_reading_time": max(5, len(full_content.split()) // 200)
        }
        
        return EducationalContent(
            title=title,
            content=full_content,
            content_type=ContentType.BIAS_AWARENESS,
            difficulty_level=difficulty_level,
            key_points=key_points,
            examples=examples,
            interactive_elements=interactive_elements,
            sources=sources,
            metadata=metadata
        )
    
    def _generate_introduction(self, topic: str, issues: List[str], level: DifficultyLevel) -> str:
        """Generate introduction section"""
        if level == DifficultyLevel.BEGINNER:
            return f"This guide will help you understand why the information about '{topic}' may be misleading or incorrect. We'll break down the issues in simple terms and show you how to spot similar problems in the future."
        elif level == DifficultyLevel.ADVANCED:
            return f"This analysis examines the misinformation patterns in '{topic}', focusing on {', '.join(issues)}. We'll explore the underlying mechanisms and provide advanced detection strategies."
        else:
            return f"Let's examine why the information about '{topic}' contains misinformation. We've identified several concerning issues: {', '.join(issues)}. This guide will help you understand these problems and learn to identify similar issues."
    
    def _generate_main_explanation(self, topic: str, issues: List[str], level: DifficultyLevel) -> str:
        """Generate main explanation content"""
        explanations = []
        
        for issue in issues:
            if "hallucination" in issue.lower():
                explanations.append("**Fabricated Information**: The content contains claims that appear to be made up or cannot be verified through reliable sources.")
            elif "adversarial" in issue.lower():
                explanations.append("**Manipulative Content**: The information seems designed to manipulate or deceive readers through specific techniques.")
            elif "bias" in issue.lower():
                explanations.append("**Biased Presentation**: The information is presented in a way that favors one perspective while ignoring others.")
            elif "pii" in issue.lower():
                explanations.append("**Privacy Concerns**: The content may contain or request personal information inappropriately.")
        
        return "\n\n".join(explanations)
    
    def _generate_red_flags_section(self, issues: List[str]) -> str:
        """Generate red flags section"""
        red_flags = [
            "• Absolute statements without evidence ('always', 'never', '100%')",
            "• Emotional language designed to provoke strong reactions",
            "• Lack of credible sources or citations",
            "• Claims that seem too good to be true",
            "• Information that contradicts established facts",
            "• Requests for personal information",
            "• Pressure to act immediately without verification"
        ]
        
        return "\n".join(red_flags)
    
    def _generate_fact_checking_guidance(self, topic: str, level: DifficultyLevel) -> str:
        """Generate fact-checking guidance"""
        if level == DifficultyLevel.BEGINNER:
            return """
1. **Check the Source**: Look for the original source of the information
2. **Search for Verification**: Use search engines to find if others have verified or debunked this
3. **Look for Expert Opinions**: Find what experts in the field say about this topic
4. **Check Multiple Sources**: Don't rely on just one source
5. **Be Skeptical**: If something seems too surprising, investigate further
"""
        else:
            return """
1. **Source Analysis**: Evaluate source credibility, expertise, and potential conflicts of interest
2. **Cross-Reference**: Compare claims across multiple independent, authoritative sources
3. **Evidence Evaluation**: Assess the quality of evidence presented (studies, data, expert consensus)
4. **Methodology Review**: For research claims, examine the methodology and peer review status
5. **Bias Assessment**: Consider potential biases in presentation and selection of information
6. **Temporal Context**: Check if information is current and relevant
7. **Expert Consultation**: Seek opinions from recognized experts in the relevant field
"""
    
    def _generate_key_points(self, issues: List[str]) -> List[str]:
        """Generate key takeaway points"""
        return [
            "Always verify information from multiple reliable sources",
            "Be skeptical of claims that seem too extreme or absolute",
            "Check the credentials and motivations of information sources",
            "Look for peer-reviewed research and expert consensus",
            "Be aware of your own biases when evaluating information",
            "Take time to fact-check before sharing information with others"
        ]
    
    def _generate_relevant_examples(self, topic: str, issues: List[str]) -> List[Dict[str, Any]]:
        """Generate relevant examples"""
        examples = []
        
        for example in self.misinformation_examples:
            if any(issue.lower() in example["category"].lower() for issue in issues):
                examples.append({
                    "title": f"Example: {example['category'].replace('_', ' ').title()}",
                    "description": example["example"],
                    "red_flags": example["red_flags"],
                    "fact_check_approach": example["fact_check_approach"]
                })
        
        return examples[:3]  # Limit to 3 most relevant examples
    
    def _generate_interactive_elements(self, topic: str, issues: List[str], level: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate interactive learning elements"""
        elements = []
        
        # Quiz questions
        elements.append({
            "type": "quiz",
            "title": "Knowledge Check",
            "questions": [
                {
                    "question": f"What are the main red flags in information about {topic}?",
                    "type": "multiple_choice",
                    "options": ["Lack of sources", "Emotional language", "Absolute claims", "All of the above"],
                    "correct": 3
                },
                {
                    "question": "What should you do before sharing information online?",
                    "type": "multiple_choice", 
                    "options": ["Share immediately", "Verify from multiple sources", "Add your opinion", "Change the wording"],
                    "correct": 1
                }
            ]
        })
        
        # Practice exercise
        elements.append({
            "type": "exercise",
            "title": "Fact-Checking Practice",
            "description": f"Practice identifying misinformation patterns in content similar to '{topic}'",
            "instructions": [
                "Read the provided example carefully",
                "Identify potential red flags",
                "List questions you would ask to verify the information",
                "Suggest reliable sources to check"
            ]
        })
        
        return elements
    
    def _compile_educational_sources(self, topic: str) -> List[str]:
        """Compile relevant educational sources"""
        return [
            "Media Literacy Now - https://medialiteracynow.org/",
            "First Draft - https://firstdraftnews.org/",
            "Poynter Institute - https://www.poynter.org/",
            "Reuters Institute - https://reutersinstitute.politics.ox.ac.uk/",
            "UNESCO Media and Information Literacy - https://en.unesco.org/themes/media-and-information-literacy"
        ]
    
    # Additional helper methods for other content types...
    def _generate_category_overview(self, category: str) -> str:
        """Generate overview for specific category"""
        overviews = {
            "health": "Health misinformation can have serious consequences. This guide will help you evaluate medical claims and identify reliable health information sources.",
            "politics": "Political information is often biased or misleading. Learn to identify partisan sources and find balanced, factual political information.",
            "technology": "Technology claims can be exaggerated or misunderstood. This guide helps you evaluate tech-related information critically.",
            "social": "Social media spreads information rapidly, but not always accurately. Learn to verify social content before believing or sharing."
        }
        return overviews.get(category, f"This guide focuses on fact-checking {category} information effectively.")
    
    def _generate_fact_checking_steps(self, category: str, level: DifficultyLevel) -> str:
        """Generate step-by-step fact-checking process"""
        steps = [
            "1. **Identify the Claim**: Clearly identify what specific claim is being made",
            "2. **Find the Original Source**: Trace back to the original source of the information",
            "3. **Evaluate Source Credibility**: Assess the reliability and expertise of the source",
            "4. **Cross-Reference**: Check multiple independent sources for the same information",
            "5. **Look for Expert Opinion**: Find what recognized experts say about the topic",
            "6. **Check for Updates**: Ensure the information is current and hasn't been superseded",
            "7. **Consider Context**: Understand the full context, not just isolated facts",
            "8. **Document Your Findings**: Keep track of your fact-checking process and sources"
        ]
        return "\n".join(steps)
    
    def _generate_fact_checking_tools(self, category: str) -> str:
        """Generate tools and resources section"""
        tools = [
            "**Search Engines**: Google, Bing for general verification",
            "**Fact-Checking Sites**: Snopes, PolitiFact, FactCheck.org",
            "**Academic Databases**: Google Scholar, PubMed (for health), JSTOR",
            "**Government Sources**: Official government websites and databases",
            "**News Verification**: AllSides, Ground News for media bias checking",
            "**Reverse Image Search**: Google Images, TinEye for image verification",
            "**Social Media Verification**: CrowdTangle, Hoaxy for social media analysis"
        ]
        return "\n".join(tools)
    
    def _generate_common_pitfalls(self, category: str) -> str:
        """Generate common pitfalls section"""
        pitfalls = [
            "• **Confirmation Bias**: Only looking for sources that confirm what you already believe",
            "• **Single Source Reliance**: Trusting only one source without verification",
            "• **Outdated Information**: Using old information that may no longer be accurate",
            "• **Misunderstanding Correlation vs Causation**: Assuming correlation implies causation",
            "• **Cherry-Picking Data**: Selecting only data that supports a particular viewpoint",
            "• **Appeal to Authority**: Accepting claims just because they come from an authority figure",
            "• **Emotional Decision Making**: Letting emotions override critical thinking"
        ]
        return "\n".join(pitfalls)
    
    def _generate_practice_exercises(self, category: str, level: DifficultyLevel) -> str:
        """Generate practice exercises"""
        exercises = [
            "**Exercise 1**: Find a recent news article in your category and trace it back to its original source",
            "**Exercise 2**: Take a controversial claim and find three different perspectives on it",
            "**Exercise 3**: Practice identifying bias in news articles by comparing coverage across different outlets",
            "**Exercise 4**: Use fact-checking websites to verify a viral social media post",
            "**Exercise 5**: Create a fact-checking checklist for your specific area of interest"
        ]
        return "\n".join(exercises)
    
    # Additional helper methods would continue here...
    def _extract_key_points_from_guide(self, category: str) -> List[str]:
        return [
            "Systematic approach is key to effective fact-checking",
            "Multiple sources provide better verification than single sources",
            "Understanding bias helps in evaluating information quality",
            "Documentation of the fact-checking process is important",
            "Regular practice improves fact-checking skills"
        ]
    
    def _get_category_examples(self, category: str) -> List[Dict[str, Any]]:
        return [ex for ex in self.misinformation_examples if category in ex["category"]]
    
    def _generate_guide_interactive_elements(self, category: str, level: DifficultyLevel) -> List[Dict[str, Any]]:
        return [
            {
                "type": "checklist",
                "title": f"{category.title()} Fact-Checking Checklist",
                "items": [
                    "Source identified and evaluated",
                    "Multiple sources consulted",
                    "Expert opinions considered",
                    "Bias assessment completed",
                    "Context fully understood"
                ]
            }
        ]
    
    def _compile_fact_checking_sources(self, category: str) -> List[str]:
        return [
            "Poynter Institute's International Fact-Checking Network",
            "Reuters Fact Check",
            "Associated Press Fact Check",
            "BBC Reality Check",
            "Snopes.com"
        ]
    
    # Bias-related helper methods...
    def _generate_bias_introduction(self, bias_types: List[str], cultural_context: str) -> str:
        return f"Bias is a natural part of human thinking, but it can lead to misinformation. In the {cultural_context} context, we'll explore {', '.join(bias_types)} and learn to recognize and mitigate their effects."
    
    def _generate_bias_type_section(self, bias_type: str, cultural_context: str, level: DifficultyLevel) -> str:
        return f"Understanding {bias_type} bias and how it manifests in {cultural_context} information sources."
    
    def _generate_bias_recognition_techniques(self, bias_types: List[str]) -> str:
        return "Learn to identify bias through language analysis, source evaluation, and perspective checking."
    
    def _generate_bias_mitigation_strategies(self, bias_types: List[str], cultural_context: str) -> str:
        return "Strategies to reduce the impact of bias in information consumption and sharing."
    
    def _generate_bias_key_points(self, bias_types: List[str]) -> List[str]:
        return [
            "Everyone has biases - awareness is the first step",
            "Seek diverse perspectives on important topics",
            "Question your initial reactions to information",
            "Use systematic approaches to evaluate information"
        ]
    
    def _generate_bias_examples(self, bias_types: List[str], cultural_context: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Example of {bias_type} bias",
                "description": f"How {bias_type} bias appears in {cultural_context} media",
                "recognition_tips": ["Look for loaded language", "Check for missing perspectives"]
            }
            for bias_type in bias_types[:3]
        ]
    
    def _generate_bias_interactive_elements(self, bias_types: List[str], level: DifficultyLevel) -> List[Dict[str, Any]]:
        return [
            {
                "type": "bias_detection_exercise",
                "title": "Spot the Bias",
                "description": "Practice identifying different types of bias in sample texts"
            }
        ]
    
    def _compile_bias_awareness_sources(self) -> List[str]:
        return [
            "Harvard's Project Implicit",
            "Cognitive Bias Codex",
            "Media Bias/Fact Check",
            "AllSides Media Bias Chart"
        ]

# Global service instance
educational_content_service = EducationalContentGenerator()

# Convenience functions
async def generate_misinformation_explanation(topic: str, 
                                            detected_issues: List[str],
                                            difficulty_level: str = "intermediate") -> EducationalContent:
    """Generate educational explanation about misinformation"""
    level = DifficultyLevel(difficulty_level.lower())
    return await educational_content_service.generate_misinformation_explanation(
        topic=topic,
        detected_issues=detected_issues,
        difficulty_level=level
    )

async def generate_fact_checking_guide(content_category: str,
                                     difficulty_level: str = "intermediate") -> EducationalContent:
    """Generate fact-checking guide for specific category"""
    level = DifficultyLevel(difficulty_level.lower())
    return await educational_content_service.generate_fact_checking_guide(
        content_category=content_category,
        difficulty_level=level
    )

async def generate_bias_awareness_content(bias_types: List[str],
                                        cultural_context: str = "indian",
                                        difficulty_level: str = "intermediate") -> EducationalContent:
    """Generate bias awareness content"""
    level = DifficultyLevel(difficulty_level.lower())
    return await educational_content_service.generate_bias_awareness_content(
        bias_types=bias_types,
        cultural_context=cultural_context,
        difficulty_level=level
    )
