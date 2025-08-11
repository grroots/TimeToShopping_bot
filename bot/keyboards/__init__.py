"""
Keyboards package for TimeToShopping_bot
Inline and reply keyboards for bot interactions
"""

from .common import (
    get_main_menu_keyboard,
    get_post_format_keyboard,
    get_post_actions_keyboard,
    get_edit_options_keyboard,
    get_confirmation_keyboard,
    get_stats_keyboard,
    get_cta_keyboard,
    get_calendar_keyboard,
    get_time_keyboard,
    get_media_type_keyboard,
    get_back_keyboard
)

__all__ = [
    "get_main_menu_keyboard",
    "get_post_format_keyboard", 
    "get_post_actions_keyboard",
    "get_edit_options_keyboard",
    "get_confirmation_keyboard",
    "get_stats_keyboard",
    "get_cta_keyboard",
    "get_calendar_keyboard",
    "get_time_keyboard", 
    "get_media_type_keyboard",
    "get_back_keyboard"
]

# Keyboard configuration
KEYBOARD_CONFIG = {
    "resize_keyboard": True,
    "one_time_keyboard": False,
    "selective": False
}

# Common button texts in Armenian
BUTTON_TEXTS = {
    # Actions
    "publish": "✅ Հրապարակել",
    "schedule": "🕒 Պլանավորել", 
    "edit": "✏️ Խմբագրել",
    "delete": "❌ Ջնջել",
    "cancel": "❌ Չեղարկել",
    "back": "🔙 Հետ",
    "confirm": "✅ Հաստատել",
    "skip": "⏭️ Բաց թողնել",
    
    # Menu items
    "new_post": "📝 Նոր փոստ",
    "stats": "📊 Վիճակագրություն",
    "drafts": "📋 Նախագծեր", 
    "scheduled": "⏰ Պլանավորված",
    "settings": "🔧 Կարգավորումներ",
    "help": "ℹ️ Օգնություն",
    
    # Post formats
    "selling_post": "🔥 Վաճառող փոստ",
    "collection_post": "📝 Ընտրանի",
    "info_post": "💡 Տեղեկատվական",
    "promo_post": "⚡ Ակցիա/Զեղչ",
    
    # Media types
    "photo": "🖼️ Նկար",
    "video": "🎥 Վիդեո", 
    "gif": "🎞️ GIF",
    "no_media": "🚫 Առանց մեդիա",
    
    # Time periods
    "today": "📅 Այսօր",
    "week": "📊 Շաբաթ",
    "month": "📈 Ամիս",
    "top_posts": "🏆 Լավագույնները",
    "formats": "📈 Ձևաչափներ",
    
    # Export
    "export_csv": "📄 CSV Export",
    "export_json": "📄 JSON Export"
}

# Emoji collections for different categories
EMOJIS = {
    "actions": ["✅", "❌", "✏️", "🕒", "🔄", "🗑️"],
    "media": ["🖼️", "🎥", "🎞️", "📁", "🎵", "📄"],
    "time": ["⏰", "📅", "⏳", "🕐", "📆", "⌛"],
    "stats": ["📊", "📈", "📉", "🏆", "📋", "💹"],
    "status": ["🟢", "🔴", "🟡", "⚫", "🔵", "🟣"],
    "navigation": ["🔙", "➡️", "⬅️", "🔼", "🔽", "🏠"]
}

def get_emoji(category: str, index: int = 0) -> str:
    """
    Get emoji from category
    
    Args:
        category: Emoji category
        index: Index of emoji in category
        
    Returns:
        Emoji string or empty string if not found
    """
    emojis = EMOJIS.get(category, [])
    return emojis[index] if 0 <= index < len(emojis) else ""

def create_callback_data(action: str, **kwargs) -> str:
    """
    Create callback data string
    
    Args:
        action: Main action
        **kwargs: Additional parameters
        
    Returns:
        Callback data string
    """
    parts = [action]
    for key, value in kwargs.items():
        parts.append(f"{key}:{value}")
    return ":".join(parts)