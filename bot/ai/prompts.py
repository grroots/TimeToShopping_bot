"""
AI Prompts for TimeToShopping_bot
Armenian language prompts for different post formats
"""

# System prompt in Armenian
SYSTEM_PROMPT_ARMENIAN = """
Դու ShoppingTime Telegram-ալիքի խմբագրիչն ես։ Գրում ես տեքստեր 4 ձևաչափով․

1. Վաճառող փոստ՝ 
   - Կպչուն վերնագիր էմոջիով (5–8 բառ)
   - 2–3 նախադասություն օգուտի մասին
   - CTA կոճակ

2. Ընտրանի՝
   - Կարճ լիդ (1 նախադասություն)
   - Ապրանքների ցանկ (3–5, ամեն մեկը էմոջիով)
   - CTA կոճակ

3. Տեղեկատվական փոստ՝
   - Վերնագիր-հարց կամ խայծ
   - 3–4 խորհուրդ կամ փաստ
   - CTA կոճակ

4. Ակցիա/զեղչ՝
   - Հրատապություն («🔥 Այսօր», «🔥 Քիչ մնաց», «🔥 Հաշված օրեր»)
   - Շահավետ առաջարկ
   - CTA կոճակ

Տեքստի երկարությունը՝ 50–90 բառ։
Լսարանը՝ ShoppingTime ալիքի հետևորդներ։
Միշտ ավարտիր CTA-ով՝ «Փնտրել նմանատիպը», «Գնել զեղչով», «Իմանալ ավելին» և այլն։
Օգտագործիր էմոջիներ, բայց չափավոր։
"""

# Post format specific prompts
POST_FORMAT_PROMPTS = {
    "selling": {
        "armenian": """
Ստեղծիր վաճառող փոստ հետևյալ կառուցվածքով:
- Կպչուն վերնագիր էմոջիով (5-8 բառ)
- 2-3 նախադասություն օգուտի և արժեքի մասին
- Ավարտիր CTA-ով («Գնել հիմա», «Փնտրել նմանատիպը»)
Տեքստը պետք է հուզական լինի և գործողության մղի:
        """,
        "cta_examples": ["Գնել հիմա", "Փնտրել նմանատիպը", "Պատվիրել զեղչով"]
    },
    
    "collection": {
        "armenian": """
Ստեղծիր ընտրանի փոստ հետևյալ կառուցվածքով:
- Կարճ ներածական նախադասություն
- 3-5 ապրանքների ցանկ, ամեն մեկը էմոջիով
- CTA գործողության համար
Ամեն տարր պետք է կարճ և պարզ լինի:
        """,
        "cta_examples": ["Տեսնել ամբողջ ընտրանին", "Ընտրել ձեզ համար", "Փնտրել ավելին"]
    },
    
    "info": {
        "armenian": """
Ստեղծիր տեղեկատվական փոստ հետևյալ կառուցվածքով:
- Վերնագիր-հարց կամ հետաքրքիր փաստ
- 3-4 օգտակար խորհուրդ կամ տեղեկություն
- CTA խորհուրդ ստանալու կամ ավելին իմանալու համար
Տեքստը պետք է կրթական և օգտակար լինի:
        """,
        "cta_examples": ["Իմանալ ավելին", "Ստանալ խորհուրդ", "Կարդալ ավելին"]
    },
    
    "promo": {
        "armenian": """
Ստեղծիր ակցիոն/զեղչային փոստ հետևյալ կառուցվածքով:
- Հրատապության վերնագիր («🔥 Այսօր», «🔥 Քիչ մնաց», «🔥 Հաշված օրեր»)
- Զեղչի կամ առաջարկի մանրամասները
- Ակտիվ CTA անմիջական գործողության համար
Տեքստը պետք է հրատապություն և FOMO ստեղծի:
        """,
        "cta_examples": ["Օգտվել հիմա", "Զեղչով գնել", "Չչափահաս առաջարկը"]
    }
}

# Default CTA buttons in Armenian
DEFAULT_CTA_BUTTONS = [
    "Փնտրել նմանատիպը",
    "Գնել զեղչով", 
    "Իմանալ ավելին",
    "Տեսնել ավելին",
    "Պատվիրել հիմա",
    "Ընտրել ձեզ համար",
    "Ստանալ խորհուրդ"
]

# Emoji sets for different post types
EMOJI_SETS = {
    "selling": ["🔥", "💥", "⭐", "🎯", "💎", "🚀"],
    "collection": ["📝", "🎁", "✨", "🌟", "📋", "🎪"],
    "info": ["💡", "📚", "🤔", "💭", "📖", "🧠"],
    "promo": ["🔥", "⚡", "💥", "🎉", "🏷️", "💸"]
}

def get_system_prompt() -> str:
    """Get the main system prompt in Armenian"""
    return SYSTEM_PROMPT_ARMENIAN

def get_user_prompt(post_format: str, keywords: str, additional_details: str = "") -> str:
    """Generate user prompt based on format and keywords"""
    
    format_instruction = POST_FORMAT_PROMPTS.get(post_format, {}).get("armenian", "")
    
    prompt = f"""
Ձևաչափ: {post_format}
Բանալի բառեր: {keywords}

{format_instruction}

{f"Լրացուցիչ մանրամասներ: {additional_details}" if additional_details else ""}

Գրիր տեքստը վերևի կանոններով։
"""
    
    return prompt.strip()

def get_cta_examples(post_format: str) -> list:
    """Get CTA examples for specific post format"""
    return POST_FORMAT_PROMPTS.get(post_format, {}).get("cta_examples", DEFAULT_CTA_BUTTONS[:3])

def get_format_emojis(post_format: str) -> list:
    """Get appropriate emojis for post format"""
    return EMOJI_SETS.get(post_format, EMOJI_SETS["selling"])

# Format display names in Armenian
FORMAT_NAMES = {
    "selling": "Վաճառող փոստ",
    "collection": "Ընտրանի", 
    "info": "Տեղեկատվական",
    "promo": "Ակցիա/Զեղչ"
}

def get_format_name(post_format: str) -> str:
    """Get format display name in Armenian"""
    return FORMAT_NAMES.get(post_format, post_format)

def get_all_formats() -> dict:
    """Get all available post formats"""
    return FORMAT_NAMES