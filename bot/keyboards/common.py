"""
Common keyboards for TimeToShopping_bot
Inline and reply keyboards for bot interactions
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from bot.ai.prompts import get_all_formats, get_cta_examples

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="📝 Նոր փոստ"),
        KeyboardButton(text="📊 Վիճակագրություն")
    )
    builder.row(
        KeyboardButton(text="📋 Նախագծեր"),
        KeyboardButton(text="⏰ Պլանավորված")
    )
    builder.row(
        KeyboardButton(text="🔧 Կարգավորումներ"),
        KeyboardButton(text="ℹ️ Օգնություն")
    )
    
    return builder.as_markup(resize_keyboard=True)

def get_post_format_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting post format"""
    builder = InlineKeyboardBuilder()
    
    formats = get_all_formats()
    format_emojis = {
        "selling": "🔥",
        "collection": "📝", 
        "info": "💡",
        "promo": "⚡"
    }
    
    for format_key, format_name in formats.items():
        emoji = format_emojis.get(format_key, "📄")
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {format_name}",
                callback_data=f"format:{format_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="❌ Չեղարկել", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_post_actions_keyboard(post_id: int, status: str = "draft") -> InlineKeyboardMarkup:
    """Keyboard for post actions (publish, edit, schedule, delete)"""
    builder = InlineKeyboardBuilder()
    
    if status == "draft":
        builder.row(
            InlineKeyboardButton(text="✅ Հրապարակել", callback_data=f"publish:{post_id}"),
            InlineKeyboardButton(text="🕒 Պլանավորել", callback_data=f"schedule:{post_id}")
        )
        builder.row(
            InlineKeyboardButton(text="✏️ Խմբագրել", callback_data=f"edit:{post_id}"),
            InlineKeyboardButton(text="❌ Ջնջել", callback_data=f"delete:{post_id}")
        )
    elif status == "scheduled":
        builder.row(
            InlineKeyboardButton(text="✅ Հրապարակել հիմա", callback_data=f"publish_now:{post_id}")
        )
        builder.row(
            InlineKeyboardButton(text="🕒 Վերապլանավորել", callback_data=f"reschedule:{post_id}"),
            InlineKeyboardButton(text="❌ Ջնջել", callback_data=f"delete:{post_id}")
        )
    elif status == "published":
        builder.row(
            InlineKeyboardButton(text="📊 Վիճակագրություն", callback_data=f"stats:{post_id}")
        )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Հետ", callback_data="back_to_main")
    )
    
    return builder.as_markup()

def get_edit_options_keyboard(post_id: int) -> InlineKeyboardMarkup:
    """Keyboard for editing options"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📝 Խմբագրել տեքստը", callback_data=f"edit_text:{post_id}"),
        InlineKeyboardButton(text="🖼️ Փոխել մեդիան", callback_data=f"edit_media:{post_id}")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Վերագեներացնել", callback_data=f"regenerate:{post_id}"),
        InlineKeyboardButton(text="🎯 Փոխել ձևաչափը", callback_data=f"change_format:{post_id}")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Ավարտել խմբագրումը", callback_data=f"finish_edit:{post_id}")
    )
    
    return builder.as_markup()

def get_confirmation_keyboard(action: str, post_id: int) -> InlineKeyboardMarkup:
    """Confirmation keyboard for actions"""
    builder = InlineKeyboardBuilder()
    
    action_texts = {
        "publish": "Հրապարակել",
        "delete": "Ջնջել",
        "schedule": "Պլանավորել"
    }
    
    action_text = action_texts.get(action, action)
    
    builder.row(
        InlineKeyboardButton(text=f"✅ Այո, {action_text.lower()}", callback_data=f"confirm_{action}:{post_id}"),
        InlineKeyboardButton(text="❌ Ոչ", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Statistics keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Այսօր", callback_data="stats:day"),
        InlineKeyboardButton(text="📊 Շաբաթ", callback_data="stats:week")
    )
    builder.row(
        InlineKeyboardButton(text="🏆 Լավագույնները", callback_data="stats:top"),
        InlineKeyboardButton(text="📈 Ձևաչափներ", callback_data="stats:formats")
    )
    builder.row(
        InlineKeyboardButton(text="📄 CSV Export", callback_data="stats:export")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Հետ", callback_data="back_to_main")
    )
    
    return builder.as_markup()

def get_cta_keyboard(post_format: str) -> InlineKeyboardMarkup:
    """Keyboard for selecting CTA button"""
    builder = InlineKeyboardBuilder()
    
    cta_examples = get_cta_examples(post_format)
    
    for cta in cta_examples:
        builder.row(
            InlineKeyboardButton(text=cta, callback_data=f"cta:{cta}")
        )
    
    builder.row(
        InlineKeyboardButton(text="✏️ Գրել ուրիշ", callback_data="cta:custom"),
        InlineKeyboardButton(text="🚫 Առանց CTA", callback_data="cta:none")
    )
    
    return builder.as_markup()

def get_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """Simple calendar keyboard for date selection"""
    builder = InlineKeyboardBuilder()
    
    # Month/Year header
    months = [
        "Հունվար", "Փետրվար", "Մարտ", "Ապրիլ", "Մայիս", "Հունիս",
        "Հուլիս", "Օգոստոս", "Սեպտեմբեր", "Հոկտեմբեր", "Նոյեմբեր", "Դեկտեմբեր"
    ]
    
    builder.row(
        InlineKeyboardButton(text="◀️", callback_data=f"cal_prev:{year}:{month}"),
        InlineKeyboardButton(text=f"{months[month-1]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal_next:{year}:{month}")
    )
    
    # Days header
    days_header = ["E", "E", "E", "C", "H", "O", "K"]  # Armenian day abbreviations
    row_buttons = []
    for day in days_header:
        row_buttons.append(InlineKeyboardButton(text=day, callback_data="ignore"))
    builder.row(*row_buttons)
    
    # Calendar days (simplified - just show 1-31)
    import calendar
    cal = calendar.monthcalendar(year, month)
    
    for week in cal:
        row_buttons = []
        for day in week:
            if day == 0:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=str(day), 
                        callback_data=f"cal_select:{year}:{month}:{day}"
                    )
                )
        builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="❌ Չեղարկել", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_time_keyboard() -> InlineKeyboardMarkup:
    """Time selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Hours
    times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", 
             "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    
    # Create rows of 3 buttons each
    for i in range(0, len(times), 3):
        row_times = times[i:i+3]
        row_buttons = [
            InlineKeyboardButton(text=time, callback_data=f"time:{time}")
            for time in row_times
        ]
        builder.row(*row_buttons)
    
    builder.row(
        InlineKeyboardButton(text="✏️ Ուրիշ ժամ", callback_data="time:custom"),
        InlineKeyboardButton(text="❌ Չեղարկել", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_media_type_keyboard() -> InlineKeyboardMarkup:
    """Media type selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🖼️ Նկար", callback_data="media:photo"),
        InlineKeyboardButton(text="🎥 Վիդեո", callback_data="media:video")
    )
    builder.row(
        InlineKeyboardButton(text="🎞️ GIF", callback_data="media:gif"),
        InlineKeyboardButton(text="🚫 Առանց մեդիա", callback_data="media:none")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Չեղարկել", callback_data="cancel")
    )
    
    return builder.as_markup()

def get_back_keyboard() -> InlineKeyboardMarkup:
    """Simple back button keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Հետ", callback_data="back_to_main")
    )
    return builder.as_markup()