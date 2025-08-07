"""
Configuration module for TimeToShopping_bot
Loads environment variables and provides configuration settings
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class with all bot settings"""
    
    # Telegram Bot Settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "@time_2_shopping")
    CHANNEL_CHAT_ID: str = os.getenv("CHANNEL_CHAT_ID", "")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "200"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bot_database.db")
    
    # Security Settings
    AUTHORIZED_USERS: List[int] = [
        int(user_id.strip()) 
        for user_id in os.getenv("AUTHORIZED_USERS", "").split(",") 
        if user_id.strip().isdigit()
    ]
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    
    # Scheduler Settings
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "Asia/Yerevan")
    
    # Health Check Settings (for deployment)
    HEALTH_CHECK_PORT: int = int(os.getenv("HEALTH_CHECK_PORT", "8000"))
    
    # Environment Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration parameters"""
        required_params = [
            ("BOT_TOKEN", cls.BOT_TOKEN),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing_params = [
            param_name for param_name, param_value in required_params 
            if not param_value
        ]
        
        if missing_params:
            raise ValueError(f"Missing required configuration parameters: {missing_params}")
        
        if not cls.AUTHORIZED_USERS:
            raise ValueError("No authorized users configured")
        
        return True
    
    @classmethod
    def is_user_authorized(cls, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        return user_id in cls.AUTHORIZED_USERS

# Validate configuration on import
config = Config()
config.validate()