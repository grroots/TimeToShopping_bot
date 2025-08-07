"""
Handlers package for TimeToShopping_bot
Contains all command and callback handlers
"""

from . import admin, analytics, scheduler

# Export all routers for easy import
__all__ = ["admin", "analytics", "scheduler"]

def register_all_handlers(dp):
    """
    Register all handlers with the dispatcher
    
    Args:
        dp: Aiogram Dispatcher instance
    """
    dp.include_router(admin.router)
    dp.include_router(analytics.router)
    dp.include_router(scheduler.router)