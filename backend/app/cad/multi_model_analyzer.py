"""
Multi-Model CAD Analyzer with Strict Vision Analysis Rules
Enforces structured 5-stage analysis with NO repetition or invented data
"""

import os
import io
import base64
import httpx
import logging
from typing import Dict, Optional
from pathlib import Path
from PIL import Image
import google.generativeai as genai

logger = logging.getLogger(__name__)

class MultiModelCADAnalyzer:
    """Advanced CAD analyzer with strict rule enforcement"""
    
    # Master system prompt enforcing all rules
    SYSTEM_PROMPT = """You are a technical CAD analysis expert. You MUST follow these rules STRICTLY:

ABSOLUTE RULES (NON-NEGOTIABLE):
1. Be CONCISE - Maximum 5-6 bullet points per stage
2. NO repetition across stages - each stage covers DIFFERENT aspects
3. NO invented data - if dimensions/standards are not visible, state "Not present in drawing"
4. NO storytelling or teaching tone - declarative statements only
5. NO "Based on the image..." prose - direct technical analysis only
6. Assume reader is a professional engineer

PROHIBITED:
- Repeating the same information in different words
- Adding extra sections beyond what's requested
- Inventing measurements, tolerances, or standards
- Using phrases like "Based on the analysis..." or "In conclusion..."

If data is missing, state it ONCE and move on. Be technical, neutral, and precise."""

    MODELS = {
        # === GOOGLE STUDIO GEMINI (PRIMARY) ===
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "provider": "GEMINI_DIRECT",
            "fallback_provider": "GEMINI_DIRECT",
            "fallback_model": "gemini-2.5-flash-lite",
            "capabilities": ["vision", "fast"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "Google AI Studio (recommended)",
            "api_model": "gemini-2.5-flash"
        },
        
        # === GOOGLE STUDIO GEMINI LITE (FALLBACK) ===
        "gemini-2.5-flash-lite": {
            "name": "Gemini 2.5 Flash Lite",
            "provider": "GEMINI_DIRECT",
            "capabilities": ["vision", "fast", "lite"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "Lighter version, better for quota limits",
            "api_model": "gemini-2.5-flash-lite"
        },
        
        # === OPENROUTER GEMINI (SECONDARY FALLBACK) ===
        "google/gemini-2.0-flash-exp:free": {
            "name": "Gemini 2.0 Flash (OpenRouter)",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "fast"],
            "context_window": "1M tokens",
            "free": True,
            "notes": "OpenRouter fallback (rate limited)"
        },
        
        # === VISION MODELS (FREE) ===
        "nvidia/nemotron-nano-12b-v2-vl:free": {
            "name": "NVIDIA Nemotron Nano VL",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "technical"],
            "context_window": "32K tokens",
            "free": True,
            "notes": "Optimized for technical diagrams"
        },
        
        "qwen/qwen-2.5-vl-7b-instruct:free": {
            "name": "Qwen 2.5 VL 7B",
            "provider": "OPENROUTER",
            "capabilities": ["vision", "fast"],
            "context_window": "32K tokens",
            "free": True,
            "notes": "Qwen vision model"
        },
        
        # === TEXT-ONLY MODELS (FREE) ===
        "meta-llama/llama-3.3-70b-instruct:free": {
            "name": "Llama 3.3 70B Instruct",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "large_context"],
            "context_window": "128K tokens",
            "free": True,
            "notes": "Best free text model"
        },
        
        "google/gemma-3-27b-it:free": {
            "name": "Gemma 3 27B IT",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "fast"],
            "context_window": "8K tokens",
            "free": True,
            "notes": "Fast Google model"
        },
        
        "openai/gpt-oss-20b:free": {
            "name": "GPT OSS 20B",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning"],
            "context_window": "16K tokens",
            "free": True,
            "notes": "Open source GPT-style"
        },
        
        # === TEXT-ONLY MODELS (PAID) ===
        "deepseek/deepseek-r1": {
            "name": "DeepSeek R1",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "advanced"],
            "context_window": "64K tokens",
            "free": False,
            "notes": "Excellent reasoning (paid)"
        },
        
        "qwen/qwen3-235b-a22b": {
            "name": "Qwen 3 235B",
            "provider": "OPENROUTER",
            "capabilities": ["reasoning", "advanced"],
            "context_window": "32K tokens",
            "free": False,
            "notes": "Large reasoning model (paid)"
        }
    }
    
    def __init__(self, gemini_api_key: str = None, openrouter_api_key: str = None):
        """Initialize with both API keys"""
        self.gemini_api_key = gemini_api_key or os.getenv('GOOGLE_API_KEY')
        self.openrouter_api_key = openrouter_api_key or os.getenv('OPENROUTER_API_KEY')
        
        # Setup Google Studio Gemini models
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_models = {
                    'gemini-2.5-flash': genai.GenerativeModel('gemini-2.5-flash'),
                    'gemini-2.5-flash-lite': genai.GenerativeModel('gemini-2.5-flash-lite')
                }
                logger.info("✅ Google Studio Gemini models initialized")
            except Exception as e:
                logger.warning(f"⚠️ Google Studio init failed: {e}")
                self.gemini_models = {}
        else:
            logger.warning("⚠️ No GOOGLE_API_KEY")
            self.gemini_models = {}
        
        if not self.openrouter_api_key:
            logger.warning("⚠️ No OPENROUTER_API_KEY - OpenRouter fallback unavailable")
    
    async def analyze_with_gemini_direct(self, image_bytes: Optional[bytes], prompt: str, model_name: str = 'gemini-2.5-flash') -> str:
        """Google Studio Gemini (PRIMARY)"""
        if model_name not in self.gemini_models:
            raise Exception(f"Gemini model {model_name} not initialized")
        
        try:
            model = self.gemini_models[model_name]
            # Prepend system prompt
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                response = model.generate_content([full_prompt, image])
            else:
                response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                raise QuotaExceededError(f"Gemini quota exceeded: {error_msg}")
            raise Exception(f"Gemini API error: {error_msg}")
    
    async def analyze_with_openrouter(self, image_bytes: Optional[bytes], prompt: str, model_id: str) -> str:
        """OpenRouter (FALLBACK + other models)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://documind.app",
                "X-Title": "DocuMind CAD Analyzer"
            }
            
            if image_bytes:
                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                message_content = [
                    {"type": "text", "text": f"{self.SYSTEM_PROMPT}\n\n{prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            else:
                message_content = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": message_content}]
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content']
                
        except httpx.HTTPStatusError as e:
            raise Exception(f"OpenRouter error ({e.response.status_code}): {e.response.text[:200]}")
        except Exception as e:
            raise Exception(f"OpenRouter failed: {e}")
    
    async def analyze_with_auto_fallback(self, image_bytes: Optional[bytes], prompt: str, model_id: str = "gemini-2.5-flash") -> tuple[str, str]:
        """Smart analysis with cascading fallback: Flash → Flash Lite → OpenRouter"""
        model_info = self.MODELS.get(model_id)
        if not model_info:
            raise ValueError(f"Unknown model: {model_id}")
        
        # GEMINI_DIRECT with cascading fallback
        if model_info['provider'] == 'GEMINI_DIRECT':
            # Try primary model first
            api_model = model_info.get('api_model', 'gemini-2.5-flash')
            try:
                logger.info(f"🔵 Trying Google Studio {api_model}...")
                response = await self.analyze_with_gemini_direct(image_bytes, prompt, api_model)
                logger.info(f"✅ Google Studio {api_model} succeeded")
                return response, f"Google Studio {api_model}"
            except QuotaExceededError as e:
                logger.warning(f"⚠️ {api_model} quota exceeded")
                
                # Try Gemini fallback (Flash Lite)
                fallback_model = model_info.get('fallback_model')
                if fallback_model and fallback_model in self.gemini_models:
                    try:
                        logger.info(f"🔄 Trying fallback: {fallback_model}...")
                        response = await self.analyze_with_gemini_direct(image_bytes, prompt, fallback_model)
                        logger.info(f"✅ Fallback {fallback_model} succeeded")
                        return response, f"Google Studio {fallback_model} (fallback)"
                    except QuotaExceededError:
                        logger.warning(f"⚠️ {fallback_model} also quota exceeded")
                    except Exception as e2:
                        logger.error(f"❌ Fallback error: {e2}")
                
                # Last resort: Try OpenRouter if available
                if self.openrouter_api_key:
                    or_fallback = "google/gemini-2.0-flash-exp:free"
                    try:
                        logger.info("🔄 Last resort: OpenRouter Gemini...")
                        response = await self.analyze_with_openrouter(image_bytes, prompt, or_fallback)
                        return response, "OpenRouter Gemini (fallback)"
                    except Exception as e3:
                        logger.error(f"❌ OpenRouter fallback failed: {e3}")
                
                # All fallbacks exhausted
                raise Exception("All Gemini sources exhausted (quota exceeded)")
                
            except Exception as e:
                logger.error(f"❌ Google Studio error: {e}")
                raise
        
        # For other models, use OpenRouter directly
        else:
            response = await self.analyze_with_openrouter(image_bytes, prompt, model_id)
            return response, model_info['name']
    
    async def comprehensive_analysis(self, png_path: str, model_id: str = "gemini-2.5-flash") -> Dict:
        """
        Run comprehensive 5-stage CAD analysis with STRICT RULE ENFORCEMENT
        
        CRITICAL: This analysis runs ONCE per document when Vision Analysis is triggered.
        Follow-up questions must reference this analysis, NOT regenerate it.
        """
        if not Path(png_path).exists():
            raise FileNotFoundError(f"PNG not found: {png_path}")
        
        model_info = self.MODELS.get(model_id)
        if not model_info or 'vision' not in model_info['capabilities']:
            raise ValueError(f"Model {model_id} doesn't support vision")
        
        logger.info(f"🔍 5-stage STRICT analysis with {model_info['name']}...")
        
        with open(png_path, 'rb') as f:
            image_bytes = f.read()
        
        provider_used = None
        
        # STRICT 5-STAGE PROMPTS (NO DEVIATION ALLOWED)
        stages = {
            "stage_1_identification": """STAGE 1 — DOCUMENT IDENTIFICATION

Analyze this CAD drawing and provide ONLY these 4 items (5-6 bullets MAX):
1. Drawing type (e.g., Block Diagram, Wiring Diagram, Floor Plan, Schematic)
2. Discipline (e.g., CCTV, Electrical, Telecom, Mechanical, Architectural)
3. 2D or 3D representation
4. Diagram intent (logical / physical / schematic / installation)

FORMAT: Use bullet points. Be concise. No explanations.""",

            "stage_2_system_overview": """STAGE 2 — SYSTEM OVERVIEW

Analyze the systems and connections. Provide ONLY:
1. What systems are present (list major systems only)
2. How they are logically connected (high-level flow)
3. Data/signal flow direction (if applicable)
4. Central nodes or hubs (if any)

FORMAT: Short paragraphs or bullets. NO repetition of Stage 1 info.""",

            "stage_3_components": """STAGE 3 — COMPONENT BREAKDOWN

List major components GROUPED BY SYSTEM. Do NOT:
- List every single component exhaustively
- Invent specifications not visible in the drawing
- Repeat information from previous stages

FORMAT: Grouped bullets only. Example:
- System A: Component 1, Component 2
- System B: Component 3, Component 4""",

            "stage_4_technical": """STAGE 4 — TECHNICAL CHARACTERISTICS

Provide ONLY these technical facts (declarative statements):
1. Complexity level (Low / Moderate / High) - based on density and interconnections
2. Scale indication (To-scale / Not-to-scale / Unknown)
3. Dimensions present? (Yes/No - do NOT invent values)
4. Tolerances present? (Yes/No)
5. Standards referenced? (Yes/No - if yes, which ones are VISIBLE)
6. Diagram type implications (e.g., "Logical diagram - not for installation")

If data is NOT present, state "Not present in drawing" ONCE.""",

            "stage_5_quality": """STAGE 5 — QUALITY & USABILITY ASSESSMENT

Assess practical usability:
1. Readability (Good / Fair / Poor - based on clarity, legibility)
2. Layout efficiency (Logical flow / Cluttered / Well-organized)
3. Information density (Appropriate / Too dense / Too sparse)
4. Practical usability for engineering tasks

Then provide:
- 2-3 CONCRETE issues (specific problems)
- 2-3 ACTIONABLE recommendations (specific improvements)

NO vague statements. Be specific."""
        }
        
        results = {}
        for i, (stage_name, prompt) in enumerate(stages.items(), 1):
            logger.info(f"  Stage {i}/5: {stage_name.replace('_', ' ').title()}...")
            response, used_provider = await self.analyze_with_auto_fallback(image_bytes, prompt, model_id)
            results[stage_name] = response
            if not provider_used:
                provider_used = used_provider
        
        # NO EXECUTIVE SUMMARY - This would violate "no second summary" rule
        # The 5 stages ARE the complete analysis
        
        return {
            "model_used": model_info['name'],
            "model_id": model_id,
            "provider_used": provider_used,
            "analysis_complete": True,
            **results
        }
    
    def format_for_rag(self, analysis_results: Dict) -> str:
        """
        Format 5-stage analysis for RAG indexing
        Maintains strict structure without repetition
        """
        provider_note = f" via {analysis_results.get('provider_used', 'unknown')}"
        
        formatted = f"""# CAD VISION ANALYSIS ({analysis_results['model_used']}{provider_note})

## STAGE 1 — DOCUMENT IDENTIFICATION
{analysis_results.get('stage_1_identification', 'N/A')}

## STAGE 2 — SYSTEM OVERVIEW
{analysis_results.get('stage_2_system_overview', 'N/A')}

## STAGE 3 — COMPONENT BREAKDOWN
{analysis_results.get('stage_3_components', 'N/A')}

## STAGE 4 — TECHNICAL CHARACTERISTICS
{analysis_results.get('stage_4_technical', 'N/A')}

## STAGE 5 — QUALITY & USABILITY ASSESSMENT
{analysis_results.get('stage_5_quality', 'N/A')}

---
Analysis completed in 5 stages. For follow-up questions, reference the above stages."""
        
        return formatted

class QuotaExceededError(Exception):
    """Raised when API quota is exceeded"""
    pass
