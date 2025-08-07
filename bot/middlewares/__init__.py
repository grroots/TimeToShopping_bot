"""
Middlewares package for TimeToShopping_bot
Access control, logging, and request processing middlewares
"""

from .access import AccessMiddleware

__all__ = ["AccessMiddleware"]

def setup_middlewares(dp):
    """
    Setup all middlewares for the dispatcher
    
    Args:
        dp: Aiogram Dispatcher instance
    """
    # Access control middleware (should be first)
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())
    
    # Add other middlewares here if needed
    # dp.message.middleware(LoggingMiddleware())
    # dp.callback_query.middleware(RateLimitMiddleware())

# Middleware configuration
MIDDLEWARE_CONFIG = {
    "access_control": {
        "enabled": True,
        "strict_mode": True,
        "log_attempts": True
    },
    "rate_limiting": {
        "enabled": False,  # Can be enabled in production
        "requests_per_minute": 30,
        "burst_limit": 5
    },
    "logging": {
        "enabled": True,
        "log_level": "INFO",
        "include_user_data": False  # For privacy
    }
}