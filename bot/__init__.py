"""
TimeToShopping_bot package
Intelligent Telegram bot for managing ShoppingTime channel with AI-powered content generation
"""

__version__ = "1.0.0"
__author__ = "TimeToShopping Team"
__description__ = "AI-powered Telegram bot for Armenian shopping channel management"

# Package metadata
PACKAGE_NAME = "TimeToShopping_bot"
CHANNEL_NAME = "ShoppingTime"
CHANNEL_USERNAME = "@time_2_shopping"

# Supported languages
SUPPORTED_LANGUAGES = ["hy", "ru", "en"]  # Armenian, Russian, English
PRIMARY_LANGUAGE = "hy"  # Armenian

# AI Configuration
DEFAULT_AI_MODEL = "gpt-4o-mini"
DEFAULT_AI_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 200

# Post formats
POST_FORMATS = {
    "selling": "🔥 Վաճառող փոստ",
    "collection": "📝 Ընտրանի", 
    "info": "💡 Տեղեկատվական",
    "promo": "⚡ Ակցիա/Զեղչ"
}

# Media types
SUPPORTED_MEDIA_TYPES = ["photo", "video", "gif"]
MAX_MEDIA_SIZE = 50 * 1024 * 1024  # 50MB

# Database
DEFAULT_DB_URL = "sqlite:///./bot_database.db"
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20

# Scheduler
DEFAULT_TIMEZONE = "Asia/Yerevan"
SCHEDULER_CHECK_INTERVAL = 60  # seconds

# Logging
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "30 days"

# Export formats
EXPORT_FORMATS = ["csv", "json", "xlsx"]

# Rate limits
MAX_POSTS_PER_DAY = 50
MAX_POSTS_PER_HOUR = 10
ANALYTICS_BATCH_SIZE = 1000