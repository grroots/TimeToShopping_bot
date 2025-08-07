"""
AI package for TimeToShopping_bot
OpenAI integration and prompt management for Armenian content generation
"""

from .openai_client import openai_client, OpenAIClient
from .prompts import (
    get_system_prompt, 
    get_user_prompt, 
    get_all_formats,
    get_format_name,
    get_cta_examples,
    get_format_emojis,
    POST_FORMAT_PROMPTS,
    DEFAULT_CTA_BUTTONS,
    EMOJI_SETS
)

__all__ = [
    "openai_client",
    "OpenAIClient", 
    "get_system_prompt",
    "get_user_prompt",
    "get_all_formats",
    "get_format_name", 
    "get_cta_examples",
    "get_format_emojis",
    "POST_FORMAT_PROMPTS",
    "DEFAULT_CTA_BUTTONS",
    "EMOJI_SETS"
]

# AI Configuration constants
AI_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 200,
    "presence_penalty": 0.1,
    "frequency_penalty": 0.1
}

# Armenian text processing utilities
def is_armenian_text(text: str) -> bool:
    """Check if text contains Armenian characters"""
    armenian_range = range(0x0530, 0x058F + 1)  # Armenian Unicode block
    return any(ord(char) in armenian_range for char in text)

def get_text_language(text: str) -> str:
    """Detect text language (simple heuristic)"""
    if is_armenian_text(text):
        return "hy"  # Armenian
    elif any(ord(char) in range(0x0400, 0x04FF + 1) for char in text):
        return "ru"  # Russian Cyrillic
    else:
        return "en"  # Default to English

def validate_armenian_post(text: str) -> dict:
    """
    Validate Armenian post content
    
    Returns:
        dict: Validation results with score and feedback
    """
    issues = []
    score = 10
    
    # Check length
    word_count = len(text.split())
    if word_count < 30:
        issues.append("Տեքստը չափազանց կարճ է")
        score -= 2
    elif word_count > 100:
        issues.append("Տեքստը չափազանց երկար է")
        score -= 1
    
    # Check Armenian content
    if not is_armenian_text(text):
        issues.append("Տեքստը չի պարունակում հայերեն բովանդակություն")
        score -= 3
    
    # Check for CTA
    cta_indicators = ["գնել", "փնտրել", "իմանալ", "ընտրել", "պատվիրել", "օգտվել"]
    has_cta = any(indicator in text.lower() for indicator in cta_indicators)
    if not has_cta:
        issues.append("Տեքստը չի պարունակում CTA")
        score -= 1
    
    # Check for emojis
    emoji_count = sum(1 for char in text if ord(char) > 0x1F600)
    if emoji_count == 0:
        issues.append("Ցանկալի է ավելացնել էմոջիներ")
        score -= 0.5
    
    return {
        "score": max(0, score),
        "issues": issues,
        "word_count": word_count,
        "has_armenian": is_armenian_text(text),
        "has_cta": has_cta,
        "emoji_count": emoji_count
    }