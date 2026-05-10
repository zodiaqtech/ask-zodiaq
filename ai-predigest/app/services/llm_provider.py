"""
LLM Provider abstraction layer with modular prompt support

This service wraps multiple LLM providers and integrates with the
domain-specific prompt builders for specialized analysis.
"""
import os
import re
import unicodedata
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging

from config.settings import get_settings
from app.domains.base import QueryMeta, TimingWindow, QueryType

settings = get_settings()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        """Generate a response from the LLM"""
        pass
    
    @staticmethod
    def to_ascii(text: str) -> str:
        """Convert text to ASCII-safe format"""
        if not text:
            return ""
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        return re.sub(r"\s+", " ", text).strip()


class GroqProvider(LLMProvider):
    """Groq LLM provider"""

    def __init__(self):
        from groq import Groq
        api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is required")
        self.client = Groq(api_key=api_key)
        self.model = settings.GROQ_MODEL

    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        is_json_mode = "OUTPUT_FORMAT: JSON" in prompt
        is_hindi = "भाषा आवश्यकता: हिंदी" in prompt or "HINDI" in prompt.upper()[:500] or "भाषा: सभी" in prompt

        if is_json_mode:
            if is_hindi:
                system_message = (
                    "आप एक विशेषज्ञ वैदिक ज्योतिषी हैं। "
                    "सभी text fields (title, impact, possible_outcomes, astrological_reasoning, evidence) "
                    "हिंदी (देवनागरी) में लिखें। "
                    "केवल valid JSON लौटाएँ, कोई अतिरिक्त text नहीं।"
                )
            else:
                system_message = (
                    "You are an expert Vedic astrologer. "
                    "Return ONLY valid JSON as specified. No extra text, no markdown."
                )
        elif is_hindi:
            system_message = """आप एक वैदिक ज्योतिषी हैं। सभी उत्तर हिंदी में लिखें।

आउटपुट फॉर्मेट:
GENERAL_ANSWER: [हिंदी में 3-5 पंक्तियाँ]
ASTROLOGICAL_ANALYSIS: [हिंदी में 8-15 पंक्तियाँ - सबसे लंबा खंड]
SUMMARY: [हिंदी में 2-3 पंक्तियाँ]
REMEDIES_ASTROLOGICAL: [हिंदी में मंत्र]
REMEDIES_GENERAL: [हिंदी में सुझाव]

सभी content हिंदी में लिखें। Headers अंग्रेजी में रखें।"""
        else:
            system_message = """You are a Vedic astrologer. Structure your response with 5 sections:
GENERAL_ANSWER: (3-5 lines)
ASTROLOGICAL_ANALYSIS: (8-15 lines - LONGEST section)
SUMMARY: (2-3 lines)
REMEDIES_ASTROLOGICAL: (bullet points)
REMEDIES_GENERAL: (bullet points)"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self):
        from openai import OpenAI
        api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=api_key)
        self.model = settings.OPENAI_MODEL
    
    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        is_json_mode = "OUTPUT_FORMAT: JSON" in prompt
        is_hindi = "भाषा आवश्यकता: हिंदी" in prompt or "HINDI" in prompt.upper()[:500] or "भाषा: सभी" in prompt

        if is_json_mode:
            if is_hindi:
                system_message = (
                    "आप एक विशेषज्ञ वैदिक ज्योतिषी हैं। "
                    "सभी text fields (title, impact, possible_outcomes, astrological_reasoning, evidence) "
                    "हिंदी (देवनागरी) में लिखें। "
                    "केवल valid JSON लौटाएँ, कोई अतिरिक्त text नहीं।"
                )
            else:
                system_message = (
                    "You are an expert Vedic astrologer. "
                    "Return ONLY valid JSON as specified. No extra text, no markdown."
                )
        elif is_hindi:
            system_message = """आप एक वैदिक ज्योतिषी हैं। आपको सभी उत्तर हिंदी (देवनागरी लिपि) में देने हैं।

आउटपुट फॉर्मेट (5 खंड अनिवार्य):

GENERAL_ANSWER:
[3-5 पंक्तियाँ - हिंदी में सीधा उत्तर]

ASTROLOGICAL_ANALYSIS:
[8-15 पंक्तियाँ - हिंदी में विस्तृत ज्योतिषीय विश्लेषण]

SUMMARY:
[2-3 पंक्तियाँ - हिंदी में संक्षिप्त निष्कर्ष]

REMEDIES_ASTROLOGICAL:
- [हिंदी में मंत्र और उपाय]

REMEDIES_GENERAL:
- [हिंदी में व्यावहारिक सुझाव]

महत्वपूर्ण: सभी खंडों में हिंदी में लिखें। Section headers अंग्रेजी में रखें।"""
        else:
            system_message = """You are a Vedic astrologer. Structure your response with ALL 5 sections:
GENERAL_ANSWER: [3-5 lines]
ASTROLOGICAL_ANALYSIS: [8-15 lines - LONGEST section]
SUMMARY: [2-3 lines - DIFFERENT from GENERAL_ANSWER]
REMEDIES_ASTROLOGICAL: [bullet points]
REMEDIES_GENERAL: [bullet points]"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI LLM provider.

    Auto-detects client mode from AZURE_OPENAI_API_VERSION:
      - API version >= 2025-xx-xx → Azure AI Foundry mode (OpenAI-compatible /openai/v1,
        no temperature, max_completion_tokens)
      - API version < 2025-xx-xx  → Classic Azure OpenAI mode (AzureOpenAI SDK,
        temperature supported, max_tokens)

    To switch models, just update the four AZURE_OPENAI_* env vars in .env.
    """

    def __init__(self):
        api_key = settings.AZURE_OPENAI_API_KEY or os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = settings.AZURE_OPENAI_ENDPOINT or os.environ.get("AZURE_OPENAI_ENDPOINT")
        deployment = settings.AZURE_OPENAI_DEPLOYMENT or os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        api_version = settings.AZURE_OPENAI_API_VERSION or os.environ.get("AZURE_OPENAI_API_VERSION", "")

        if not all([api_key, endpoint, deployment]):
            raise ValueError("Azure OpenAI requires API_KEY, ENDPOINT, and DEPLOYMENT")

        # Foundry mode: API versions from 2025 onwards use the OpenAI-compatible endpoint
        version_year = int(api_version[:4]) if api_version and api_version[:4].isdigit() else 0
        self.foundry_mode = version_year >= 2025

        if self.foundry_mode:
            from openai import OpenAI
            base_url = endpoint.rstrip("/") + "/openai/v1"
            self.client = OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"🔵 Azure Foundry mode: {base_url}, deployment={deployment}")
        else:
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            logger.info(f"🟢 Azure Classic mode: {endpoint}, deployment={deployment}, api_version={api_version}")

        self.deployment = deployment

    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        is_json_mode = "OUTPUT_FORMAT: JSON" in prompt
        is_hindi = "भाषा आवश्यकता: हिंदी" in prompt or "HINDI" in prompt.upper()[:500] or "भाषा: सभी" in prompt
        logger.info(f"🌐 Azure OpenAI ({'Foundry' if self.foundry_mode else 'Classic'}): Hindi={is_hindi}, JSON mode={is_json_mode}")

        if is_json_mode:
            if is_hindi:
                logger.info("📝 Using HINDI JSON system message")
                system_message = (
                    "आप एक विशेषज्ञ वैदिक ज्योतिषी हैं। "
                    "सभी text fields (title, impact, possible_outcomes, astrological_reasoning, evidence) "
                    "हिंदी (देवनागरी) में लिखें। "
                    "केवल valid JSON लौटाएँ, कोई अतिरिक्त text नहीं।"
                )
            else:
                logger.info("📝 Using ENGLISH JSON system message")
                system_message = (
                    "You are an expert Vedic astrologer. "
                    "Return ONLY valid JSON as specified. No extra text, no markdown."
                )
        elif is_hindi:
            logger.info("📝 Using HINDI system message")
            system_message = """आप एक वैदिक ज्योतिषी हैं। आपको सभी उत्तर हिंदी (देवनागरी लिपि) में देने हैं।

आउटपुट फॉर्मेट (5 खंड अनिवार्य):

GENERAL_ANSWER:
[3-5 पंक्तियाँ - हिंदी में सीधा उत्तर]

ASTROLOGICAL_ANALYSIS:
[8-15 पंक्तियाँ - हिंदी में विस्तृत ज्योतिषीय विश्लेषण]
उदाहरण: "सप्तम भाव का स्वामी शुक्र वक्री है और षष्ठम भाव में स्थित है..."

SUMMARY:
[2-3 पंक्तियाँ - हिंदी में संक्षिप्त निष्कर्ष]

REMEDIES_ASTROLOGICAL:
- [हिंदी में मंत्र और उपाय]

REMEDIES_GENERAL:
- [हिंदी में व्यावहारिक सुझाव]

महत्वपूर्ण नियम:
1. सभी खंडों में हिंदी में लिखें (देवनागरी लिपि)
2. Section headers अंग्रेजी में रखें (GENERAL_ANSWER:, etc.)
3. ग्रहों के नाम: सूर्य, चंद्र, मंगल, बुध, गुरु, शुक्र, शनि, राहु, केतु
4. ASTROLOGICAL_ANALYSIS सबसे लंबा खंड होना चाहिए
5. SUMMARY और GENERAL_ANSWER अलग-अलग होने चाहिए"""
        else:
            logger.info("📝 Using ENGLISH system message")
            system_message = """You are a Vedic astrologer who writes detailed astrological analyses.

You MUST structure your response with ALL 5 sections:
GENERAL_ANSWER: [3-5 lines]
ASTROLOGICAL_ANALYSIS: [8-15 lines - LONGEST section]
SUMMARY: [2-3 lines - DIFFERENT from GENERAL_ANSWER]
REMEDIES_ASTROLOGICAL: [bullet points]
REMEDIES_GENERAL: [bullet points]

CRITICAL: ASTROLOGICAL_ANALYSIS must be LONGEST. SUMMARY must be SHORT and UNIQUE."""

        kwargs = dict(
            model=self.deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
        )
        if self.foundry_mode:
            # Foundry models (e.g. gpt-5.2) don't support temperature
            kwargs["max_completion_tokens"] = max_tokens
        else:
            # Classic Azure models (e.g. gpt-4o) support temperature + max_tokens
            kwargs["temperature"] = temperature
            kwargs["max_tokens"] = max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self):
        import anthropic
        api_key = settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = settings.ANTHROPIC_MODEL
    
    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        is_json_mode = "OUTPUT_FORMAT: JSON" in prompt
        is_hindi = "भाषा आवश्यकता: हिंदी" in prompt or "HINDI" in prompt.upper()[:500] or "भाषा: सभी" in prompt

        if is_json_mode:
            if is_hindi:
                system_message = (
                    "आप एक विशेषज्ञ वैदिक ज्योतिषी हैं। "
                    "सभी text fields (title, impact, possible_outcomes, astrological_reasoning, evidence) "
                    "हिंदी (देवनागरी) में लिखें। "
                    "केवल valid JSON लौटाएँ, कोई अतिरिक्त text नहीं।"
                )
            else:
                system_message = (
                    "You are an expert Vedic astrologer. "
                    "Return ONLY valid JSON as specified. No extra text, no markdown."
                )
        elif is_hindi:
            system_message = """आप एक वैदिक ज्योतिषी हैं। सभी उत्तर हिंदी (देवनागरी लिपि) में लिखें।

आउटपुट फॉर्मेट:
GENERAL_ANSWER: [हिंदी में 3-5 पंक्तियाँ]
ASTROLOGICAL_ANALYSIS: [हिंदी में 8-15 पंक्तियाँ - सबसे लंबा खंड]
SUMMARY: [हिंदी में 2-3 पंक्तियाँ]
REMEDIES_ASTROLOGICAL: [हिंदी में मंत्र]
REMEDIES_GENERAL: [हिंदी में सुझाव]

सभी content हिंदी में लिखें। Headers अंग्रेजी में रखें।"""
        else:
            system_message = """You are a Vedic astrologer. Structure your response with 5 sections:
GENERAL_ANSWER, ASTROLOGICAL_ANALYSIS (longest), SUMMARY, REMEDIES_ASTROLOGICAL, REMEDIES_GENERAL."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_message,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self):
        import google.generativeai as genai
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate(self, prompt: str, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        # Check if Hindi is requested in the prompt
        is_hindi = "भाषा आवश्यकता: हिंदी" in prompt or "HINDI" in prompt.upper()[:500]
        
        if is_hindi:
            system_prefix = """आप एक वैदिक ज्योतिषी हैं। सभी उत्तर हिंदी में लिखें।
आउटपुट: GENERAL_ANSWER, ASTROLOGICAL_ANALYSIS, SUMMARY, REMEDIES_ASTROLOGICAL, REMEDIES_GENERAL
सभी content हिंदी में। Headers अंग्रेजी में।

"""
            prompt = system_prefix + prompt
        
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )
        return response.text


def get_llm_provider() -> LLMProvider:
    """Factory function to get the configured LLM provider"""
    provider_name = settings.LLM_PROVIDER.lower()
    
    providers = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
        "azure_openai": AzureOpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
    
    return providers[provider_name]()


class ModularLLMService:
    """
    Service wrapper for LLM operations with modular prompt support.
    
    This service uses domain-specific prompt builders when available,
    falling back to generic prompts otherwise.
    """
    
    def __init__(self):
        self._provider: Optional[LLMProvider] = None
    
    @property
    def provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = get_llm_provider()
        return self._provider
    
    def _format_vedic_planets_for_llm(self, planets: Dict, houses: List) -> str:
        """
        Format Vedic planet data in a clear, readable format for LLM.
        This ensures the LLM can easily reference correct house placements.
        Now includes DETERMINISTIC aspect calculations to prevent hallucination.
        """
        if not planets:
            return ""
        
        # Import aspect calculation function
        try:
            from app.utils.vedic_api_parser import calculate_planetary_aspects, format_aspects_for_llm
            aspects_available = True
        except ImportError:
            aspects_available = False
            logger.warning("Could not import aspect calculation functions")
        
        lines = []
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " " * 15 + "🔴 AUTHORITATIVE PLANETARY POSITIONS 🔴" + " " * 23 + "║")
        lines.append("╠" + "═" * 78 + "╣")
        lines.append("║ CRITICAL: These are the CORRECT positions from the birth chart.              ║")
        lines.append("║ If ANY other data conflicts with these positions, IGNORE THE OTHER DATA.     ║")
        lines.append("║ Technical points may contain outdated/incorrect positions - DO NOT USE THEM. ║")
        lines.append("╚" + "═" * 78 + "╝")
        lines.append("")
        lines.append("VERIFIED PLANET PLACEMENTS (USE THESE ONLY):")
        lines.append("-" * 60)
        
        for planet_name, data in planets.items():
            if isinstance(data, dict):
                house = data.get("house", "?")
                sign = data.get("sign", data.get("zodiac", "?"))
                retro = " ⟲ RETROGRADE" if data.get("is_retro") or data.get("retro") else ""
                nakshatra = data.get("nakshatra", "")
                nak_str = f" in {nakshatra}" if nakshatra else ""
                
                lines.append(f"  ★ {planet_name}: HOUSE {house}, {sign}{nak_str}{retro}")
        
        lines.append("")
        lines.append("HOUSE LORDSHIPS:")
        lines.append("-" * 60)
        
        if houses:
            for h in houses:
                if isinstance(h, dict):
                    house_num = h.get("house", "?")
                    sign = h.get("sign", h.get("start_rasi", "?"))
                    lord = h.get("sign_lord", h.get("rashi_lord", "?"))
                    planets_in = h.get("planets", [])
                    
                    planets_str = f" → Contains: {', '.join(planets_in)}" if planets_in else ""
                    lines.append(f"  • House {house_num}: {sign} (Lord = {lord}){planets_str}")
        
        # ✅ ADD DETERMINISTIC ASPECT CALCULATIONS
        if aspects_available:
            try:
                aspects_data = calculate_planetary_aspects(planets)
                aspects_block = format_aspects_for_llm(aspects_data, planets)
                lines.append(aspects_block)
                logger.info(f"✅ Added deterministic aspects for {len(planets)} planets")
            except Exception as e:
                logger.warning(f"Failed to calculate aspects: {e}")
                lines.append("")
                lines.append("⚠️ Aspect calculation unavailable - DO NOT assume any aspects.")
        
        lines.append("")
        lines.append("═" * 78)
        lines.append("⚠️  OVERRIDE RULE: When technical points mention a planet's house, sign, or aspect,")
        lines.append("    ALWAYS use the positions and aspects listed above instead. The technical points")
        lines.append("    may contain KP/calculation data that differs from the actual birth chart.")
        lines.append("═" * 78)
        
        return "\n".join(lines)

    def _format_vedic_planets_for_mental_health(self, planets: Dict, houses: List) -> str:
        """
        Format planet data for Q3 Mental Health — Vedic Sign Lord only.
        NO KP framing, NO 'IGNORE THE OTHER DATA' override language.
        Focuses only on emotional wellness planets: Moon, Mercury, Rahu, Ketu.
        """
        if not planets:
            return ""

        lines = []
        lines.append("═" * 70)
        lines.append("🌙 VEDIC BIRTH CHART DATA — EMOTIONAL WELLNESS ANALYSIS")
        lines.append("   (Use these positions for Moon, Mercury, Rahu, 4th/5th house lords)")
        lines.append("═" * 70)
        lines.append("")

        # Planet placements — all planets for reference
        lines.append("PLANETARY PLACEMENTS (Vedic Sign Lord system):")
        lines.append("-" * 50)
        HINDI = {
            "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल", "Mercury": "बुध",
            "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि",
            "Rahu": "राहु", "Ketu": "केतु"
        }
        for planet_name, data in planets.items():
            if planet_name in ("Uranus", "Neptune", "Pluto", "Ascendant"):
                continue  # skip modern/outer planets for Vedic mental health
            if isinstance(data, dict):
                house = data.get("house", "?")
                sign = data.get("sign", "?")
                nakshatra = data.get("nakshatra", "")
                retro = " (वक्री)" if data.get("is_retro") else ""
                combust = " (अस्त)" if data.get("is_combusted") else ""
                hindi = HINDI.get(planet_name, planet_name)
                nak_str = f", {nakshatra} नक्षत्र" if nakshatra else ""
                lines.append(f"  • {planet_name} ({hindi}): भाव {house}, {sign} राशि{nak_str}{retro}{combust}")

        lines.append("")
        lines.append("HOUSE LORDSHIPS (भाव स्वामी):")
        lines.append("-" * 50)
        if houses:
            for h in houses:
                if isinstance(h, dict):
                    house_num = h.get("house", "?")
                    sign = h.get("sign", "?")
                    lord = h.get("sign_lord", h.get("rashi_lord", "?"))
                    planets_in = h.get("planets", [])
                    planets_str = f" — ग्रह: {', '.join(planets_in)}" if planets_in else ""
                    lines.append(f"  • भाव {house_num} ({sign}): स्वामी {lord}{planets_str}")

        lines.append("")
        lines.append("═" * 70)
        lines.append("📌 KEY PLANETS FOR EMOTIONAL WELLNESS (use data above):")
        lines.append("   Moon (चंद्र) placement and sign → primary mind indicator")
        lines.append("   Mercury (बुध) — combust/retro? → nervous system clarity")
        lines.append("   Rahu house → mental restlessness tendency")
        lines.append("   4th house lord → emotional peace capacity")
        lines.append("   5th house lord → mental joy and intellect")
        lines.append("═" * 70)

        return "\n".join(lines)

    def _strip_kp_from_mental_health(self, text: str) -> str:
        """
        Post-process Q3 Mental Health LLM output to remove any KP CSL content
        the model hallucinated despite prompt instructions.
        Replaces KP sections with Vedic-only content markers.
        """
        import re

        # Extract ASTROLOGICAL_ANALYSIS section to clean it
        analysis_match = re.search(
            r'(ASTROLOGICAL_ANALYSIS:\s*)(.*?)(\n(?:SUMMARY|REMEDIES_ASTROLOGICAL|REMEDIES_GENERAL):)',
            text, re.DOTALL | re.IGNORECASE
        )
        if not analysis_match:
            return text

        original_analysis = analysis_match.group(2)
        cleaned = original_analysis

        # 1. Remove entire KP CSL header blocks with their content
        # Matches 【KP CSL विश्लेषण】 ... up to next 【 or Vedic section
        cleaned = re.sub(
            r'【KP CSL[^】]*】.*?(?=【वैदिक|【Vedic|\*\*वैदिक|\*\*Vedic|$)',
            '', cleaned, flags=re.DOTALL | re.IGNORECASE
        )

        # 2. Remove tier headers 【स्तर 1/2/3】 lines and their content blocks
        cleaned = re.sub(
            r'【स्तर\s*\d[^】]*】[^\n]*\n?(?:(?!【|\*\*[1-9]|\n\n).)*',
            '', cleaned, flags=re.DOTALL
        )

        # 3. Remove individual CSL bullet lines: "- षष्ठ भाव CSL: ..."
        cleaned = re.sub(
            r'[-•]\s*\*?\*?(?:षष्ठ|अष्टम|द्वादश|एकादश|प्रथम|पंचम)\s+भाव\s+(?:का\s+)?CSL[^\n]*\n?',
            '', cleaned, flags=re.IGNORECASE
        )

        # 4. Remove lines containing "signify" in any form (KP terminology)
        cleaned = re.sub(r'[^\n]*signify\s+(?:करता|करती|करते)[^\n]*\n?', '', cleaned)
        cleaned = re.sub(r'[^\n]*signifies\s+houses[^\n]*\n?', '', cleaned)
        cleaned = re.sub(r'[^\n]*को\s+signify\s+कर[^\n]*\n?', '', cleaned)
        cleaned = re.sub(r'[^\n]*\bsignify\b[^\n]*\n?', '', cleaned)

        # 5. Remove CSL chain lines: "श्रृंखला: ... → नक्षत्र स्वामी ..."
        cleaned = re.sub(r'[^\n]*श्रृंखला[^\n]*\n?', '', cleaned)

        # 6. Remove any remaining "KP" references in analysis
        cleaned = re.sub(r'[^\n]*\bKP\b[^\n]*\n?', '', cleaned)

        # 7. Remove lines with "CSL" anywhere
        cleaned = re.sub(r'[^\n]*\bCSL\b[^\n]*\n?', '', cleaned)

        # 8. Clean up extra blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()

        if cleaned != original_analysis:
            logger.info(f"🧹 KP filter: removed {len(original_analysis) - len(cleaned)} chars of KP content from Q3")

        # Also clean GENERAL_ANSWER: replace forbidden phrases
        text_with_clean_analysis = text[:analysis_match.start(2)] + cleaned + text[analysis_match.end(2):]

        # Fix forbidden phrases in general_answer and summary too
        text_with_clean_analysis = text_with_clean_analysis.replace(
            "पेशेवर सहायता लेना अत्यंत महत्वपूर्ण है",
            "यदि लक्षण बने रहें तो किसी विशेषज्ञ से परामर्श उपयोगी हो सकता है"
        )
        text_with_clean_analysis = text_with_clean_analysis.replace(
            "पेशेवर सहायता लेना अत्यंत आवश्यक है",
            "यदि लक्षण बने रहें तो किसी विशेषज्ञ से परामर्श उपयोगी हो सकता है"
        )
        text_with_clean_analysis = text_with_clean_analysis.replace(
            "पेशेवर चिकित्सा सहायता लेना अत्यंत महत्वपूर्ण है",
            "यदि मन अत्यधिक भारी लगे तो किसी विश्वसनीय परामर्शदाता से बात करना उपयोगी हो सकता है"
        )
        text_with_clean_analysis = text_with_clean_analysis.replace(
            "पेशेवर चिकित्सा सहायता लेना अत्यंत आवश्यक है",
            "यदि मन अत्यधिक भारी लगे तो किसी विश्वसनीय परामर्शदाता से बात करना उपयोगी हो सकता है"
        )

        return text_with_clean_analysis

    def analyze_with_prompt_builder(
        self,
        prompt_builder,
        question: str,
        technical_points: List[str],
        meta: QueryMeta,
        timing_windows: Optional[List[Dict]] = None,
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        language: str = "Hindi",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate analysis using a domain-specific prompt builder.
        
        Args:
            prompt_builder: The domain-specific prompt builder instance
            question: User's question
            technical_points: Technical astrological points from evaluator
            meta: Query metadata
            timing_windows: Optional timing windows for TIMING queries
            planets: Optional planet data
            houses: Optional house data
            language: Output language - "Hindi" or "English" (default)
            **kwargs: Additional parameters (sub_subdomain, compatibility_data, etc.)
        
        Returns:
            Parsed response with general_answer, analysis, remedies, etc.
        """
        # Pass timing windows as-is (dicts or TimingWindow objects)
        # Prompt builders handle both formats correctly
        
        # ✅ LOG planets being sent to LLM for debugging
        if planets:
            planet_summary = []
            for pname, pdata in list(planets.items())[:5]:  # Show first 5 planets
                if isinstance(pdata, dict):
                    house = pdata.get("house", "?")
                    sign = pdata.get("sign", pdata.get("zodiac", "?"))
                    planet_summary.append(f"{pname}:H{house}/{sign}")
            logger.info(f"🌟 VEDIC planets for LLM: {', '.join(planet_summary)}")
        else:
            logger.warning("⚠️ No planets data sent to LLM - positions may be missing!")
        
        # ✅ PREPEND Vedic planetary positions BEFORE the main prompt
        # This ensures LLM sees correct positions FIRST and uses them as primary source
        vedic_planet_block = ""
        if planets:
            vedic_planet_block = self._format_vedic_planets_for_llm(planets, houses) + "\n\n"
        
        # Build the prompt using the domain-specific builder
        # ✅ Extract dasha context from kwargs
        current_dasha = kwargs.get('current_dasha')
        dasha_timeline = kwargs.get('dasha_timeline')
        lalkitab_remedies_context = kwargs.get('lalkitab_remedies_context', '')

        # Log what we received
        if current_dasha:
            logger.info(f"📊 Current dasha for prompt: {current_dasha.get('dasha_name', 'Unknown')}")
        else:
            logger.warning("⚠️ No current_dasha received")

        if dasha_timeline:
            logger.info(f"📊 Timeline for prompt: "
                    f"{len(dasha_timeline.get('past_2_years', []))} past, "
                    f"{len(dasha_timeline.get('next_10_years', []))} future")
        else:
            logger.warning("⚠️ No dasha_timeline received")
        
        if lalkitab_remedies_context:
            logger.info(f"🔮 Lal Kitab remedies context provided ({len(lalkitab_remedies_context)} chars)")
        
        # Build the prompt using the domain-specific builder
        prompt = prompt_builder.build_analysis_prompt(
            question=question,
            technical_points=technical_points,
            meta=meta,
            timing_windows=timing_windows,
            planets=planets,
            houses=houses,
            language=language,
            **kwargs
        )

        # ── MINOR GUARD: sentinel check ───────────────────────────────────────
        if prompt.startswith("FINAL_RESPONSE::"):
            import json as _json
            logger.warning(
                "[LLM_PROVIDER] 🚨 FINAL_RESPONSE sentinel detected — "
                "skipping LLM call (minor user)"
            )
            final_data = _json.loads(prompt[len("FINAL_RESPONSE::"):])
            return {
                "general_answer": final_data.get("general_answer", ""),
                "astrological_analysis": final_data.get("astrological_analysis"),
                "summary": final_data.get("summary"),
                "remedies_astrological": [],
                "remedies_general": [],
                "timing_windows": final_data.get("timing_windows"),
                "overview_summary": final_data.get("overview_summary"),
            }
        # ── END MINOR GUARD ───────────────────────────────────────────────────
        
        # Combine: Vedic block FIRST, then main prompt, then Lal Kitab remedies context at the end
        is_mental_health = "Mental Health" in str(kwargs.get("sub_subdomain", ""))
        if is_mental_health and planets:
            # ✅ For Q3 Mental Health: use Vedic-only planet block (no KP framing, no IGNORE override)
            mental_health_planet_block = self._format_vedic_planets_for_mental_health(planets, houses or [])
            prompt = mental_health_planet_block + "\n\n" + prompt
        elif vedic_planet_block:
            # Standard KP+Vedic planet block for all other questions
            prompt = vedic_planet_block + prompt
        
        # ✅ NEW: Append Lal Kitab remedies context for remedy generation
        if lalkitab_remedies_context:
            prompt = prompt + "\n\n" + lalkitab_remedies_context
        
        # DEBUG: Log full prompt for Q3 mental health (first 3000 chars)
        if "Mental Health" in str(kwargs.get("sub_subdomain", "")) or "mental_health" in str(kwargs.get("sub_subdomain", "")).lower():
            logger.info(f"🧠 Q3 MENTAL HEALTH PROMPT (first 3000 chars):\n{'='*60}\n{prompt[:3000]}\n{'='*60}")

        # Generate response
        text = self.provider.generate(prompt, temperature=settings.LLM_TEMPERATURE)

        # DEBUG: Log raw LLM response (first 500 chars)
        logger.info(f"🔍 RAW LLM RESPONSE (first 500 chars):\n{text[:500] if text else 'EMPTY'}")
        logger.info(f"🔍 Response length: {len(text) if text else 0} chars")

        # Check if Hindi characters are present in raw response
        hindi_chars = [c for c in text if '\u0900' <= c <= '\u097F'] if text else []
        logger.info(f"🔍 Hindi characters in response: {len(hindi_chars)} chars")
        if hindi_chars[:20]:
            logger.info(f"🔍 Sample Hindi chars: {''.join(hindi_chars[:20])}")

        # ⛔ POST-PROCESS: Strip KP CSL content from Q3 Mental Health responses
        if is_mental_health and text:
            text = self._strip_kp_from_mental_health(text)
            logger.info("🧠 Q3 Mental Health: KP post-processing filter applied")

        # Parse response
        return self._parse_response(text)
    
    def rephrase_with_llm(
        self,
        question: str,
        points: List[str],
        domain: str,
        subtopic: str,
        meta: Dict[str, Any],
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        timing_windows: Optional[List] = None,
        language: str = "Hindi",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use LLM to generate natural language answers.
        
        This method tries to use domain-specific prompt builders first,
        falling back to generic prompts if no builder is found.
        
        Args:
            language: Output language - "Hindi" or "English" (default)
        """
        from app.domains.registry import get_prompt_builder
        
        # Try to get domain-specific prompt builder
        prompt_builder = get_prompt_builder(domain, subtopic)

        print("🔥 LLM SERVICE HIT")
        
        # DEBUG: Log what we're looking for and what we found
        logger.info(f"=== LLM SERVICE DEBUG ===")
        logger.info(f"Looking for prompt builder: domain={domain}, subtopic={subtopic}")
        logger.info(f"Prompt builder found: {prompt_builder}")
        logger.info(f"Output language: {language}")
        if prompt_builder:
            logger.info(f"Prompt builder type: {type(prompt_builder).__name__}")
        logger.info(f"kwargs keys: {kwargs.keys()}")
        if 'kundali_milan_data' in kwargs:
            logger.info(f"kundali_milan_data present in kwargs: {bool(kwargs['kundali_milan_data'])}")
        logger.info(f"=== END LLM SERVICE DEBUG ===")
        
        # Convert meta dict to QueryMeta if needed
        if isinstance(meta, dict):
            query_meta = QueryMeta.from_dict(meta)
        else:
            query_meta = meta
        
        if prompt_builder:
            logger.debug(f"Using {domain}/{subtopic} prompt builder")
            return self.analyze_with_prompt_builder(
                prompt_builder=prompt_builder,
                question=question,
                technical_points=points,
                meta=query_meta,
                timing_windows=timing_windows,
                planets=planets,
                houses=houses,
                language=language,
                **kwargs
            )
        else:
            logger.debug(f"No prompt builder for {domain}/{subtopic}, using generic")
            return self._generic_rephrase(
                question=question,
                points=points,
                domain=domain,
                subtopic=subtopic,
                meta=meta if isinstance(meta, dict) else meta.to_dict(),
                planets=planets,
                houses=houses,
                timing_windows=timing_windows,
                language=language
            )
    
    def _generic_rephrase(
        self,
        question: str,
        points: List[str],
        domain: str,
        subtopic: str,
        meta: Dict[str, Any],
        planets: Optional[Dict] = None,
        houses: Optional[List] = None,
        timing_windows: Optional[List] = None,
        language: str = "Hindi"
    ) -> Dict[str, Any]:
        """Generic rephrasing when no domain-specific prompt builder exists"""
        from datetime import datetime
        
        raw_points = "\n".join(points) if points else ""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Build language instruction
        language_instruction = ""
        if language == "Hindi":
            language_instruction = """
╔════════════════════════════════════════════════════════════════════════╗
║                    भाषा आवश्यकता: हिंदी (HINDI)                         ║
╠════════════════════════════════════════════════════════════════════════╣
║ CRITICAL: Write ALL content in Hindi (Devanagari script)               ║
║                                                                        ║
║ ✓ Section headers MUST remain in English (GENERAL_ANSWER:, etc.)      ║
║ ✓ ALL content text MUST be in Hindi देवनागरी लिपि में                  ║
║                                                                        ║
║ Planet names in Hindi:                                                 ║
║   Sun=सूर्य, Moon=चंद्र, Mars=मंगल, Mercury=बुध                        ║
║   Jupiter=गुरु/बृहस्पति, Venus=शुक्र, Saturn=शनि                       ║
║   Rahu=राहु, Ketu=केतु                                                 ║
║                                                                        ║
║ Technical terms: दशा, गोचर, भाव, राशि, नक्षत्र, कुंडली, योग           ║
╚════════════════════════════════════════════════════════════════════════╝

EXAMPLE OUTPUT IN HINDI:
GENERAL_ANSWER:
आपके विवाह के लिए अनुकूल समय 2026-2027 में है।

ASTROLOGICAL_ANALYSIS:
सप्तम भाव और शुक्र का विश्लेषण शुभ संकेत देता है।

SUMMARY:
शुभ समय निकट है।
"""
        else:
            language_instruction = """
========================================
LANGUAGE REQUIREMENT: ENGLISH
========================================
- Write ALL output in clear, professional English
- Use standard astrological terminology
========================================
"""
        
        # ✅ ALWAYS include planet/house data when provided - this is from Vedic API
        # and should be the PRIMARY source for planetary positions
        planet_block = ""
        if planets:
            planet_block = "\n" + self._format_vedic_planets_for_llm(planets, houses) + "\n"
        
        timing_block = ""
        if meta.get("type") == "TIMING" and timing_windows and len(timing_windows) > 0:
            windows_text = []
            for i, w in enumerate(timing_windows[:5]):
                start = w.get("start", "")
                end = w.get("end", "")
                dasha = w.get("dasha", "")
                score = w.get("score", 0)
                transit_score = w.get("transit_score")
                final_score = w.get("final_score")
                
                if final_score and transit_score:
                    score_str = f"base: {score}, transit: {transit_score:.1f}, FINAL: {final_score:.1f}"
                else:
                    score_str = f"strength: {score}"
                
                windows_text.append(f"  WINDOW {i+1}: {start} to {end} | {dasha} | {score_str}")
            
            # Get best window
            best = timing_windows[0]
            best_start = best.get("start", "")
            best_end = best.get("end", "")
            best_dasha = best.get("dasha", "")
            
            timing_block = f"""
{'='*70}
CALCULATED TIMING WINDOWS - YOU MUST USE THESE EXACT DATES
{'='*70}

*** BEST WINDOW: {best_start} to {best_end} ({best_dasha}) ***

ALL WINDOWS:
{chr(10).join(windows_text)}

{'='*70}
MANDATORY: 
- Your GENERAL_ANSWER MUST start with the date range: "{best_start} to {best_end}"
- DO NOT say "1-2 years" or "next few years" - use the EXACT dates above
- Your SUMMARY must include the specific date range
{'='*70}
"""
        elif meta.get("type") == "TIMING":
            timing_block = """
╔════════════════════════════════════════════════════════════════════════╗
║            ⚠️ CRITICAL: NO TIMING WINDOWS CALCULATED ⚠️                 ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  The timing calculation did NOT find favorable periods.                ║
║                                                                        ║
║  YOU MUST NOT:                                                         ║
║  ❌ Invent or make up ANY specific dates                               ║
║  ❌ Say things like "March 2026" or "next 6 months"                    ║
║  ❌ Provide ANY date ranges whatsoever                                 ║
║                                                                        ║
║  YOU MUST:                                                             ║
║  ✓ State that timing data is NOT available for this query              ║
║  ✓ Recommend detailed consultation for precise timing                  ║
║  ✓ Focus on general chart analysis and remedies                        ║
║                                                                        ║
║  ⚠️ If you invent dates, you are LYING to the user!                    ║
╚════════════════════════════════════════════════════════════════════════╝
"""
        
        prompt = f"""
You are an expert KP + Vedic astrologer.

{language_instruction}

{planet_block}

QUERY_CLASSIFICATION:
- Domain: {domain}
- Subtopic: {subtopic}
- Query_Type: {meta.get("type", "NON_TIMING")}
- Event_Polarity: {meta.get("polarity", "NEUTRAL")}
- Interpretation_Goal: {meta.get("goal", "STATUS")}
- CURRENT_DATE: {today_str}

A user asked:
"{question}"

Below are the technical astrology points generated by the system.
NOTE: If these points mention planetary positions that conflict with the AUTHORITATIVE 
positions above, IGNORE the technical point positions and use the verified positions.

TECHNICAL_POINTS:
{raw_points}

{timing_block}

DATA USAGE HIERARCHY (MANDATORY):
1. PLANETARY POSITIONS block above is the PRIMARY source - use these exact house placements.
2. TIMING_WINDOWS (if present) contain the calculated favorable periods - USE THEM.
3. TECHNICAL_POINTS provide analysis context but planetary positions in them may be outdated.
4. Do NOT invent planets, houses, or combinations not present in the data.

========================================
CRITICAL: 5 SEPARATE SECTIONS REQUIRED
========================================

YOU MUST WRITE EXACTLY 5 SEPARATE SECTIONS.
WRITING EVERYTHING IN ONE SECTION IS WRONG AND UNACCEPTABLE.

EACH SECTION MUST:
1. Start with its section header (GENERAL_ANSWER:, ASTROLOGICAL_ANALYSIS:, etc.)
2. Have its own unique content
3. NOT repeat content from other sections
4. NOT include content that belongs in other sections

========================================
SECTION REQUIREMENTS (MANDATORY):
========================================

SECTION 1 - GENERAL_ANSWER:
Header: GENERAL_ANSWER:
Length: 3-7 lines ONLY
Content: Brief direct answer to the question
Include: Main point, key finding, score (if applicable)
Do NOT include: Detailed planetary analysis, remedies, or summary

SECTION 2 - ASTROLOGICAL_ANALYSIS:
Header: ASTROLOGICAL_ANALYSIS:
Length: 8-15 lines (this is the MAIN detailed section)
Content: Detailed planetary reasoning with specific positions
Include: Houses, signs, aspects, planetary strengths, specific logic
Do NOT include: General answer or summary

SECTION 3 - SUMMARY:
Header: SUMMARY:
Length: 2-3 lines ONLY
Content: Actionable next steps with key remedy
Include: What to DO next, specific action items
Do NOT include: Repeat of general answer or full analysis

SECTION 4 - REMEDIES_ASTROLOGICAL:
Header: REMEDIES_ASTROLOGICAL:
Format: Bullet list (3-5 items)
Content: Specific astrological remedies
One remedy per line with hyphen

SECTION 5 - REMEDIES_GENERAL:
Header: REMEDIES_GENERAL:
Format: Bullet list (3-4 items)
Content: Lifestyle recommendations
One recommendation per line with hyphen

========================================
CRITICAL RULE: WRITE SECTIONS SEPARATELY
========================================

DO THIS (CORRECT):
GENERAL_ANSWER:
Short answer here.

ASTROLOGICAL_ANALYSIS:
Detailed analysis here with planets and houses.

SUMMARY:
Action steps here.

DO NOT DO THIS (WRONG):
GENERAL_ANSWER:
Short answer. Detailed analysis. Action steps. Remedies.
(Everything in one section - THIS IS WRONG!)

========================================
EXAMPLE OF CORRECT FORMAT:
========================================

GENERAL_ANSWER:
Your compatibility score is 22/36, indicating an average match. The Nadi koota scores 8/8 but Bhakoot scores 0/7 creating challenges.

ASTROLOGICAL_ANALYSIS:
The Nadi koota scores 8/8, suggesting excellent health compatibility and strong progeny potential. Gana koota scores 5/6 indicating good temperament compatibility. However, Bhakoot koota scores 0/7 due to Leo-Virgo rasi combination, creating financial challenges. Yoni koota scores 2/4 showing moderate physical compatibility. Both partners have Chandra Manglik Dosha with Mars in 12th house (boy) and 4th house (girl), which partially neutralizes but requires remedies.

SUMMARY:
Proceed with marriage after performing Bhakoot Dosha Nivaran Puja and Manglik Shanti remedies. Focus on joint financial planning and consult astrologer for optimal muhurat timing.

REMEDIES_ASTROLOGICAL:
- Perform Bhakoot Dosha Nivaran Puja monthly
- Chant Hanuman Chalisa daily for Mars pacification
- Wear Red Coral after consultation
- Conduct Navagraha Shanti Puja before marriage

REMEDIES_GENERAL:
- Practice joint financial planning
- Maintain open communication
- Engage in couple meditation
- Build trust through shared activities

========================================
FORMATTING RULES:
========================================

1. Each section MUST start with its header
2. Add blank line after each section
3. Do NOT use **, ---, or === between sections
4. Write ASTROLOGICAL_ANALYSIS as the longest section
5. Keep GENERAL_ANSWER and SUMMARY short
6. Use hyphens for remedies lists

========================================
IF YOU WRITE EVERYTHING IN GENERAL_ANSWER,
YOUR RESPONSE IS INVALID AND WILL BE REJECTED.
SEPARATE THE SECTIONS PROPERLY!
========================================
"""
        
        text = self.provider.generate(prompt, temperature=settings.LLM_TEMPERATURE)
        return self._parse_response(text)
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        # First, clean up any markdown or dividers the LLM might have added
        text = self._cleanup_llm_output(text)
        
        # Check if LLM followed the format
        has_general = "GENERAL_ANSWER:" in text
        has_analysis = "ASTROLOGICAL_ANALYSIS:" in text
        has_summary = "SUMMARY:" in text
        
        logger.info(f"📋 Format check - GENERAL: {has_general}, ANALYSIS: {has_analysis}, SUMMARY: {has_summary}")
        
        if not has_analysis:
            logger.warning("⚠️ LLM DID NOT include ASTROLOGICAL_ANALYSIS header!")
        
        # Use careful extraction
        general = self._extract_and_clean_section(text, "GENERAL_ANSWER")
        analysis = self._extract_and_clean_section(text, "ASTROLOGICAL_ANALYSIS")
        summary = self._extract_and_clean_section(text, "SUMMARY")
        
        raw_astro = self._extract_and_clean_section(text, "REMEDIES_ASTROLOGICAL").split("\n")
        raw_gen = self._extract_and_clean_section(text, "REMEDIES_GENERAL").split("\n")
        
        remedies_astro = [r.replace("- ", "").strip() for r in raw_astro if r.strip()]
        remedies_general = [r.replace("- ", "").strip() for r in raw_gen if r.strip()]
        
        # Log extraction results
        logger.info(f"📊 Extracted lengths - GENERAL: {len(general)} chars, ANALYSIS: {len(analysis)} chars, SUMMARY: {len(summary)} chars")
        
        # DETECT GENERIC PLACEHOLDER in analysis (common LLM mistake)
        generic_patterns = [
            "planetary positions indicate",
            "placement of significators",
            "interactions with other celestial",
            "key factors include",
            "The analysis shows"
        ]
        analysis_is_generic = analysis and any(pattern.lower() in analysis.lower() for pattern in generic_patterns)
        
        if analysis_is_generic:
            logger.warning("⚠️ ASTROLOGICAL_ANALYSIS contains generic placeholder text!")
        
        # DETECT if summary is duplicate of general
        summary_is_duplicate = summary and general and (
            summary == general or 
            len(summary) > 500 and summary[:200] == general[:200]
        )
        
        if summary_is_duplicate:
            logger.warning("⚠️ SUMMARY is duplicating GENERAL_ANSWER!")
        
        # FIX: If analysis is generic but general has detailed content
        if analysis_is_generic and len(general) > 400:
            logger.info("🔄 Fixing: Swapping content - general has the detailed analysis")
            # general has the real analysis, we need to restructure
            general, analysis, summary = self._emergency_restructure(general, "", "")
        
        # FIX: If summary is duplicate, create a short summary instead
        if summary_is_duplicate or (summary and len(summary) > 400):
            logger.info("🔄 Fixing: Creating short summary from content")
            # Extract first meaningful sentence for summary
            first_sentence = general.split('।')[0] if '।' in general else general.split('.')[0]
            summary = first_sentence[:200] + "..." if len(first_sentence) > 200 else first_sentence
        
        if len(general) > len(analysis) and len(general) > 400:
            logger.error(f"❌ CRITICAL: GENERAL_ANSWER ({len(general)}) is LONGER than ASTROLOGICAL_ANALYSIS ({len(analysis)})!")
            logger.error("   LLM violated format - dumped everything in GENERAL_ANSWER")
        
        # EMERGENCY FALLBACK: If analysis or summary is empty but general_answer is very long,
        # the LLM probably put everything in general_answer. Aggressively extract it.
        if (not analysis or not summary) and general and len(general) > 400:
            logger.warning(f"LLM put everything in GENERAL_ANSWER ({len(general)} chars), using emergency restructure")
            general, analysis, summary = self._emergency_restructure(general, analysis, summary)
        
        # Final safety check: if summary is still empty, create a basic one
        if not summary and (general or analysis):
            summary = "Follow the recommended remedies and maintain a balanced approach to navigate this period effectively."
        
        return {
            "general_answer": general,
            "astrological_analysis": analysis,
            "summary": summary,
            "remedies_astrological": remedies_astro,
            "remedies_general": remedies_general
        }
    
    def _cleanup_llm_output(self, text: str) -> str:
        """Remove markdown and formatting that LLM added despite instructions"""
        # Note: We keep ** (bold) for emphasized words, but remove at start of sections
        
        # Remove markdown headers
        text = re.sub(r'###\s+', '', text)
        text = re.sub(r'##\s+', '', text)
        text = re.sub(r'#\s+', '', text)
        
        # Remove horizontal dividers
        text = re.sub(r'-{3,}', '', text)
        text = re.sub(r'={3,}', '', text)
        text = re.sub(r'_{3,}', '', text)
        
        # DO NOT remove main section headers - we need them for parsing!
        # Only remove duplicate/extra labels that might appear INSIDE sections
        # Pattern: Remove ** around section headers but KEEP the headers
        text = re.sub(r'\*\*\s*(GENERAL_ANSWER|ASTROLOGICAL_ANALYSIS|SUMMARY|REMEDIES_ASTROLOGICAL|REMEDIES_GENERAL)\s*:\s*\*\*', r'\1:', text, flags=re.IGNORECASE)
        
        # Remove ** that appears right after a section header
        text = re.sub(r'((?:GENERAL_ANSWER|ASTROLOGICAL_ANALYSIS|SUMMARY|REMEDIES_ASTROLOGICAL|REMEDIES_GENERAL):\s*)\*\*\s*', r'\1', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_and_clean_section(self, text: str, label: str) -> str:
        """Extract a section and clean it carefully"""
        # Extract content between this label and the next MAIN section label ONLY
        # Be more careful - only stop at section headers at the START of a line
        pattern = rf"{label}:\s*(.*?)(?=\n\s*(?:GENERAL_ANSWER|ASTROLOGICAL_ANALYSIS|SUMMARY|REMEDIES_ASTROLOGICAL|REMEDIES_GENERAL)\s*:|$)"
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if not m:
            return ""
        
        content = m.group(1).strip()
        
        # Only clean the most obvious issues:
        # 1. Remove ** at the very start (before any text)
        content = re.sub(r'^\s*\*\*\s+', '', content)
        
        # 2. Remove standalone section labels that appear on their own line at the start
        # (But NOT words like "analysis" in normal sentences)
        content = re.sub(r'^(?:ASTROLOGICAL_)?(?:ANALYSIS|REMEDIES|SUMMARY)\s*:\s*', '', content, flags=re.IGNORECASE)
        
        # 3. Don't remove "By focusing on..." - it might be valid summary content
        
        # NOTE: Do NOT call to_ascii() here - it strips Hindi/Devanagari characters!
        # Just normalize whitespace while preserving Unicode
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def _emergency_restructure(self, general: str, analysis: str, summary: str) -> tuple:
        """
        Emergency fix when LLM dumps everything in GENERAL_ANSWER
        Intelligently splits the content into proper sections
        """
        logger.warning(f"🚨 EMERGENCY RESTRUCTURE TRIGGERED - LLM violated format")
        logger.warning(f"   Original: general={len(general)}, analysis={len(analysis)}, summary={len(summary)}")
        
        # All content is in general_answer
        all_content = general.strip()
        
        # Split by paragraphs (double newlines)
        paragraphs = [p.strip() for p in all_content.split('\n\n') if p.strip() and len(p) > 30]
        
        if len(paragraphs) == 0:
            # Single block - split by sentences
            sentences = [s.strip() + '.' for s in all_content.split('. ') if s.strip()]
            
            if len(sentences) >= 5:
                # Enough sentences to split
                general_new = '. '.join(sentences[:3])  # First 3 sentences
                analysis_new = '. '.join(sentences[3:-2])  # Middle sentences
                summary_new = '. '.join(sentences[-2:])  # Last 2 sentences
            else:
                # Very short response
                general_new = sentences[0] if sentences else "Analysis based on chart factors."
                analysis_new = '. '.join(sentences[1:-1]) if len(sentences) > 2 else (sentences[1] if len(sentences) > 1 else "")
                summary_new = sentences[-1] if sentences else "Follow recommended remedies."
        
        elif len(paragraphs) == 1:
            # One long paragraph - split by sentences
            sentences = [s.strip() + '.' for s in paragraphs[0].split('. ') if s.strip()]
            
            if len(sentences) >= 6:
                general_new = '. '.join(sentences[:3])  # First 3
                analysis_new = '. '.join(sentences[3:-2])  # Middle bulk
                summary_new = '. '.join(sentences[-2:])  # Last 2
            else:
                general_new = sentences[0] if sentences else paragraphs[0][:200]
                analysis_new = '. '.join(sentences[1:-1]) if len(sentences) > 2 else ""
                summary_new = sentences[-1] if sentences else "Follow recommended approach."
        
        elif len(paragraphs) == 2:
            # Two paragraphs - first is general, second is analysis
            general_new = paragraphs[0]
            
            # Split second paragraph - most goes to analysis, last sentence to summary
            sentences = [s.strip() + '.' for s in paragraphs[1].split('. ') if s.strip()]
            if len(sentences) >= 3:
                analysis_new = '. '.join(sentences[:-2])
                summary_new = '. '.join(sentences[-2:])
            else:
                analysis_new = paragraphs[1]
                summary_new = "Focus on the recommended remedies and practices."
        
        else:
            # Multiple paragraphs (3+) - good structure
            # First 1-2 paragraphs = GENERAL_ANSWER
            if len(paragraphs[0]) < 400:
                general_new = paragraphs[0]
                start_idx = 1
            else:
                # First paragraph too long - take first 2-3 sentences
                sentences = paragraphs[0].split('. ')
                general_new = '. '.join(sentences[:3]) + '.'
                # Put rest back
                paragraphs[0] = '. '.join(sentences[3:])
                start_idx = 0
            
            # Last paragraph = SUMMARY (if short enough)
            if len(paragraphs[-1]) < 250:
                summary_new = paragraphs[-1]
                end_idx = -1
            else:
                # Extract last 2 sentences from last paragraph
                sentences = paragraphs[-1].split('. ')
                if len(sentences) >= 3:
                    summary_new = '. '.join(sentences[-2:])
                    paragraphs[-1] = '. '.join(sentences[:-2])
                else:
                    summary_new = paragraphs[-1]
                end_idx = None
            
            # Middle paragraphs = ASTROLOGICAL_ANALYSIS
            if end_idx == -1:
                analysis_new = '\n\n'.join(paragraphs[start_idx:-1])
            else:
                analysis_new = '\n\n'.join(paragraphs[start_idx:])
        
        # Ensure none are empty
        if not general_new or len(general_new) < 20:
            general_new = "Based on the astrological analysis of your chart, here are the key insights."
        
        if not analysis_new or len(analysis_new) < 50:
            analysis_new = "The planetary positions indicate specific influences on your life path. Key factors include the placement of significators and their interactions with other celestial bodies."
        
        if not summary_new or len(summary_new) < 20:
            summary_new = "Follow the recommended remedies and maintain a balanced approach for best results."
        
        logger.info(f"   After restructure: general={len(general_new)}, analysis={len(analysis_new)}, summary={len(summary_new)}")
        
        return general_new, analysis_new, summary_new
    
    def generate_dasha_events(
        self,
        planet_details: Dict,
        past_dasha: List,
        future_dasha: List,
        language: str = "Hindi",
        lagna: str = "",
        planets: Optional[List] = None,
        houses: Optional[Dict] = None,
        age: Optional[int] = None,
        past_1year_dasha: Optional[List] = None,
    ) -> Dict[str, Any]:
        """Generate past events and dasha analysis using LLM with rich Vedic chart context."""
        import json

        is_hindi = language.strip().lower() == "hindi"

        # Use last 1 year of dasha for past events (more practical/actionable)
        past_for_events = past_1year_dasha if past_1year_dasha else past_dasha
        past_d = json.dumps(past_for_events, default=str)
        future_d = json.dumps(future_dasha[:20], default=str)  # limit future to 20 periods
        pdata = json.dumps(planet_details, default=str)

        # Build chart summary for richer context
        chart_context_lines = []
        if lagna:
            chart_context_lines.append(f"Lagna (Ascendant): {lagna}")
        if age is not None:
            chart_context_lines.append(f"Current Age: {age} years")
        if planets:
            planet_lines = []
            for p in planets[:12]:
                name = p.get("name") or p.get("planet", "")
                house = p.get("house") or p.get("house_number", "")
                sign = p.get("sign") or p.get("rashi", "")
                strength = p.get("strength") or p.get("shadbala", "")
                retrograde = p.get("is_retrograde") or p.get("retrograde", False)
                afflicted = p.get("is_afflicted") or p.get("afflicted", False)
                if name:
                    line = f"  {name}: House {house}, Sign {sign}"
                    if strength:
                        line += f", Strength: {strength}"
                    if retrograde:
                        line += ", Retrograde"
                    if afflicted:
                        line += ", Afflicted"
                    planet_lines.append(line)
            if planet_lines:
                chart_context_lines.append("Planet Positions:\n" + "\n".join(planet_lines))
        if houses:
            ownership_lines = []
            for h, data in list(houses.items())[:12]:
                lord = data.get("lord") or data.get("house_lord", "")
                if lord:
                    ownership_lines.append(f"  House {h}: lord = {lord}")
            if ownership_lines:
                chart_context_lines.append("House Ownership:\n" + "\n".join(ownership_lines))

        chart_context = "\n".join(chart_context_lines) if chart_context_lines else "(chart data not available)"

        if is_hindi:
            lang_instruction = "भाषा: सभी text, title, impact, possible_outcomes, astrological_reasoning, और evidence हिंदी (देवनागरी) में लिखें।"
            past_events_instruction = (
                "PAST_EVENTS (पिछले 1 वर्ष के दशा अनुक्रम के आधार पर 3-5 महत्वपूर्ण जीवन घटनाएँ):\n"
                "- स्वास्थ्य समस्याएँ, रिश्ते में बदलाव (ब्रेकअप / विवाह), नौकरी बदलाव, यात्रा, वित्तीय उतार-चढ़ाव आदि जैसी वास्तविक जीवन घटनाएँ बताएँ।\n"
                "- ग्रह स्थिति, लग्न, गृह स्वामित्व, और दशा के आधार पर घटनाओं का अनुमान लगाएँ।\n"
                "- आयु के अनुसार घटनाएँ व्यावहारिक होनी चाहिए।\n"
                "- प्रत्येक घटना को एक विशिष्ट दशा अवधि से जोड़ें।"
            )
            dasha_instruction = (
                "DASHA_ANALYSIS (पिछले और आने वाले दशा काल का विश्लेषण):\n"
                "- प्रत्येक दशा का 2-3 पंक्तियों में प्रभाव बताएँ।\n"
                "- सामान्य वैदिक अर्थ उपयोग करें।"
            )
        else:
            lang_instruction = "Language: Write all text fields in English."
            past_events_instruction = (
                "PAST_EVENTS (3-5 significant life events based on last 1 year dasha sequence):\n"
                "- Identify real-life events like health issues, relationship changes (breakup/marriage), job changes, travel, financial shifts.\n"
                "- Derive events from planetary positions, Lagna, house ownership, strengths/afflictions, and dasha sequence.\n"
                "- Events must be age-appropriate and practically actionable.\n"
                "- Each event must be tied to a specific dasha period."
            )
            dasha_instruction = (
                "DASHA_ANALYSIS (past and upcoming dasha periods):\n"
                "- Give 2-3 lines of impact per dasha period.\n"
                "- Use general Vedic meanings only."
            )

        prompt = f"""OUTPUT_FORMAT: JSON
You are an expert Vedic astrologer specializing in practical, actionable life event prediction.
Use ONLY the data provided below. Do NOT invent planets, houses, dashas, or dates.

{lang_instruction}

=== BIRTH CHART CONTEXT ===
{chart_context}

=== PLANET DETAILS (Vedic API) ===
{pdata}

=== PAST 1 YEAR DASHA SEQUENCE ===
{past_d}

=== UPCOMING DASHA PERIODS ===
{future_d}

=== YOUR TASK ===

1. {past_events_instruction}

2. {dasha_instruction}

OUTPUT JSON FORMAT (RETURN ONLY THIS JSON, no extra text):
{{
  "past_events_raw": [
    {{
      "title": "string",
      "date_range": {{ "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }},
      "possible_outcomes": "string",
      "astrological_reasoning": "string",
      "evidence": "string"
    }}
  ],
  "dasha_past_raw": [
    {{
      "dasha_name": "string",
      "date_range": {{ "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }},
      "impact": "string"
    }}
  ],
  "dasha_future_raw": [
    {{
      "dasha_name": "string",
      "date_range": {{ "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }},
      "impact": "string"
    }}
  ]
}}

ONLY return the JSON above.
"""

        raw = self.provider.generate(prompt, temperature=settings.LLM_TEMPERATURE)

        try:
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r"```json?", "", raw)
                raw = raw.replace("```", "")
            data = json.loads(raw)
        except Exception as e:
            logger.warning(f"Failed to parse dasha events JSON: {e}")
            data = {
                "past_events_raw": [],
                "dasha_past_raw": [],
                "dasha_future_raw": []
            }

        return {
            "past_events_raw": data.get("past_events_raw", []),
            "dasha_past_raw": data.get("dasha_past_raw", []),
            "dasha_future_raw": data.get("dasha_future_raw", [])
        }


# Singleton instance
llm_service = ModularLLMService()