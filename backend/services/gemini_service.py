"""
Gemini AI Service for enhanced domain detection and recommendations.

This module provides LLM-powered analysis using Google's Gemini API:
- Smarter domain identification
- Context-aware recommendations
- Quality Plan insights

Falls back to keyword-based analysis if API is unavailable.
"""

import os
import json
from google import genai
from google.genai import types
from config import Config


# Initialize Gemini API
def _initialize_gemini():
    """Initialize Gemini API with key from environment."""
    api_key = Config.GEMINI_API_KEY
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            return client
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            return None
    return None


# Get Gemini client
GEMINI_CLIENT = _initialize_gemini()
GEMINI_AVAILABLE = GEMINI_CLIENT is not None


def detect_domain_with_gemini(text, classified_requirements):
    """
    Use Gemini to detect the software domain from SRS content.
    
    Args:
        text: Full SRS document text
        classified_requirements: List of classified requirement dictionaries
        
    Returns:
        dict with {domain, confidence, critical_categories, reasoning} or None if failed
    """
    if not GEMINI_AVAILABLE:
        return None
        
    try:
        # Build category summary
        categories = {}
        for req in classified_requirements:
            cat = req.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        prompt = f"""You are analyzing a Software Requirements Specification (SRS) document.

Document Preview (first 2000 chars):
{text[:2000]}

Requirements Category Distribution:
{json.dumps(categories, indent=2)}

Common domains include (but you can identify others):
- Banking/Finance
- Healthcare  
- E-commerce
- Education/LMS
- Library Management
- Government/Public Sector
- IoT/Embedded
- Telecom/Networking
- Hotel/Hospitality
- Restaurant/Food Service
- HR/Payroll
- Inventory/Warehouse
- Zoo/Wildlife Management
- Transportation/Logistics
- Real Estate/Property
- Gaming/Entertainment
- Social Media
- CRM/Sales
- Manufacturing
- Agriculture
- Insurance
- Legal/Law
- Energy/Utilities
- Aviation/Airline
- Sports/Fitness

Your task:
1. Identify the MOST LIKELY domain (you may identify ANY relevant domain, not limited to the list)
2. Rate your confidence: High (0.8-1.0), Medium (0.5-0.79), Low (0-0.49)
3. Identify which ISO/IEC 9126 categories are CRITICAL for this domain
4. Provide brief reasoning

Respond in this EXACT JSON format:
{{
    "domain": "Domain Name",
    "confidence": 0.85,
    "critical_categories": ["Functionality", "Security"],
    "reasoning": "Brief explanation (1-2 sentences)"
}}"""

        response = GEMINI_CLIENT.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        result_text = response.text.strip()
        
        # Extract JSON from potential markdown code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        # Validate response
        if "domain" in result and "confidence" in result:
            return result
            
        return None
        
    except Exception as e:
        print(f"Gemini domain detection error: {e}")
        return None


def generate_recommendations_with_gemini(srs_summary, domain_info):
    """
    Use Gemini to generate enhanced recommendations based on SRS analysis.
    
    Args:
        srs_summary: Dict with category_scores, categories_present, categories_missing
        domain_info: Dict with domain, confidence, critical_categories
        
    Returns:
        list of recommendation dicts with {category, priority, suggestion, ai_powered} or None if failed
    """
    if not GEMINI_AVAILABLE:
        return None
        
    try:
        prompt = f"""You are a software quality expert analyzing an SRS document.

Domain: {domain_info.get('domain', 'Unknown')}
Confidence: {domain_info.get('confidence', 0.0)}
Critical Categories for this domain: {', '.join(domain_info.get('critical_categories', []))}

Categories Present: {', '.join(srs_summary.get('categories_present', []))}
Categories Missing: {', '.join(srs_summary.get('categories_missing', []))}

Category Distribution:
{json.dumps(srs_summary.get('category_scores', {}), indent=2)}

ISO/IEC 9126 Categories:
- Functionality: Core features and capabilities
- Reliability: Error handling, recovery, fault tolerance
- Usability: User interface, accessibility, learnability
- Efficiency: Performance, resource usage, scalability
- Maintainability: Code quality, modularity, documentation
- Portability: Platform independence, installability
- Security: Authentication, authorization, data protection

Your task:
Generate 3-5 specific, actionable recommendations to improve this SRS. Focus on:
1. Missing critical categories (HIGH priority)
2. Weak categories (MEDIUM priority)
3. Domain-specific improvements (varies by context)

For each recommendation, provide:
- category: Which ISO 9126 category it addresses
- priority: "Critical", "High", "Medium", or "Low"
- suggestion: Specific, actionable advice (1-2 sentences)

Respond in this EXACT JSON format:
{{
    "recommendations": [
        {{
            "category": "Category Name",
            "priority": "Critical|High|Medium|Low",
            "suggestion": "Specific actionable suggestion..."
        }}
    ]
}}"""

        response = GEMINI_CLIENT.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        result_text = response.text.strip()
        
        # Extract JSON from potential markdown code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        if "recommendations" in result:
            # Mark as AI-powered
            for rec in result["recommendations"]:
                rec["ai_powered"] = True
            return result["recommendations"]
            
        return None
        
    except Exception as e:
        print(f"Gemini recommendations error: {e}")
        return None


def analyze_quality_plan_with_gemini(qp_text, srs_summary, srs_domain):
    """
    Use Gemini to analyze a Quality Plan against SRS.
    
    Args:
        qp_text: Full Quality Plan text
        srs_summary: Dict with SRS analysis results
        srs_domain: Dict with domain info from SRS
        
    Returns:
        dict with {domain, suggestions, strengths, gaps} or None if failed
    """
    if not GEMINI_AVAILABLE:
        return None
        
    try:
        prompt = f"""You are a QA expert analyzing a Quality Plan document.

SRS Domain: {srs_domain.get('domain', 'Unknown')}
SRS Categories Present: {', '.join(srs_summary.get('categories_present', []))}
SRS Categories Missing: {', '.join(srs_summary.get('categories_missing', []))}

Quality Plan (first 2000 chars):
{qp_text[:2000]}

Your task:
1. Detect the Quality Plan's domain
2. Compare it to the SRS domain ({srs_domain.get('domain', 'Unknown')})
3. Identify what the QP does well (strengths)
4. Identify what's missing or weak (gaps)
5. Generate specific improvement suggestions

Respond in this EXACT JSON format:
{{
    "domain": "Detected domain",
    "domain_matches_srs": true/false,
    "strengths": ["Strength 1", "Strength 2"],
    "gaps": ["Gap 1", "Gap 2"],
    "suggestions": ["Suggestion 1", "Suggestion 2"]
}}"""

        response = GEMINI_CLIENT.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        result_text = response.text.strip()
        
        # Extract JSON from potential markdown code blocks
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        if "domain" in result:
            return result
            
        return None
        
    except Exception as e:
        print(f"Gemini QP analysis error: {e}")
        return None
