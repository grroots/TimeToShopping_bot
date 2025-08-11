"""
Access control middleware for TimeToShopping_bot
Restricts bot usage to authorized users only
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from config import config  # ИСПРАВЛЕНО: убрал bot.
from logging_config import logger  # ИСПРАВЛЕНО: убрал bot.

class AccessMiddleware(BaseMiddleware):
    """Middleware to control access to the bot"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Check if user is authorized to use the bot"""
        
        user = None
        
        # Extract user from different event types
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        
        if not user:
            # If we can't determine the user, block the request
            logger.warning("Could not determine user from event")
            return
        
        # Check if user is authorized
        if not config.is_user_authorized(user.id):
            logger.warning(
                f"Unauthorized access attempt from user {user.id} "
                f"(@{user.username}, {user.first_name} {user.last_name or ''})"
            )
            
            # Send unauthorized message
            if isinstance(event, Message):
                await event.answer(
                    "❌ Դուք չունեք այս բոտը օգտագործելու թույլտվություն։\n"
                    "Unauthorized access. Contact administrator.",
                    show_alert=True if isinstance(event, CallbackQuery) else False
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "❌ Դուք չունեք այս բոտը օգտագործելու թույլտվություն։",
                    show_alert=True
                )
            
            return  # Block further processing
        
        # Log authorized access
        logger.debug(
            f"Authorized user {user.id} (@{user.username}) accessed bot"
        )
        
        # Add user info to data for handlers
        data["user"] = user
        
        # Continue processing
        return await handler(event, data)