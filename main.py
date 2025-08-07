"""
Main entry point for TimeToShopping_bot
Initializes and starts the Telegram bot
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import config
from bot.logging_config import logger
from bot.database.db import db
from bot.middlewares.access import AccessMiddleware
from bot.handlers import admin, analytics, scheduler
from bot.utils.scheduler import scheduler_manager
from bot.ai.openai_client import openai_client

class BotApplication:
    """Main bot application class"""
    
    def __init__(self):
        # Initialize bot with default properties
        self.bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Initialize dispatcher with memory storage
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Setup middlewares
        self.setup_middlewares()
        
        # Register handlers
        self.register_handlers()
    
    def setup_middlewares(self):
        """Setup bot middlewares"""
        # Access control middleware
        self.dp.message.middleware(AccessMiddleware())
        self.dp.callback_query.middleware(AccessMiddleware())
        
        logger.info("Middlewares configured")
    
    def register_handlers(self):
        """Register all bot handlers"""
        # Register routers
        self.dp.include_router(admin.router)
        self.dp.include_router(analytics.router)
        self.dp.include_router(scheduler.router)
        
        logger.info("Handlers registered")
    
    async def on_startup(self):
        """Bot startup tasks"""
        try:
            # Initialize database
            await db.init_db()
            logger.info("Database initialized")
            
            # Test OpenAI connection
            openai_test = await openai_client.test_connection()
            if not openai_test:
                logger.warning("OpenAI connection test failed - text generation may not work")
            
            # Start scheduler
            await scheduler_manager.start()
            logger.info("Scheduler started")
            
            # Set bot commands
            await self.set_bot_commands()
            
            # Get bot info
            bot_info = await self.bot.get_me()
            logger.info(f"Bot started: @{bot_info.username}")
            
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise
    
    async def on_shutdown(self):
        """Bot shutdown tasks"""
        try:
            # Stop scheduler
            await scheduler_manager.stop()
            logger.info("Scheduler stopped")
            
            # Close database connections
            await db.close()
            logger.info("Database connections closed")
            
            # Close bot session
            await self.bot.session.close()
            logger.info("Bot session closed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    async def set_bot_commands(self):
        """Set bot commands menu"""
        from aiogram.types import BotCommand
        
        commands = [
            BotCommand(command="start", description="Սկսել աշխատանքը"),
            BotCommand(command="new_post", description="Ստեղծել նոր փոստ"),
            BotCommand(command="drafts", description="Նախագծեր"),
            BotCommand(command="scheduled", description="Պլանավորված փոստեր"),
            BotCommand(command="stats", description="Վիճակագրություն"),
            BotCommand(command="help", description="Օգնություն"),
        ]
        
        await self.bot.set_my_commands(commands)
        logger.info("Bot commands set")
    
    async def start_polling(self):
        """Start bot with polling"""
        try:
            await self.on_startup()
            logger.info("Starting bot polling...")
            await self.dp.start_polling(self.bot, allowed_updates=self.dp.resolve_used_update_types())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            raise
        finally:
            await self.on_shutdown()

# Health check server for deployment platforms
async def health_check(request):
    """Health check endpoint for Railway/Render"""
    return web.Response(text="OK", status=200)

@asynccontextmanager
async def create_app():
    """Create web application with health check"""
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)  # Root endpoint
    
    yield app

async def start_web_server():
    """Start web server for health checks"""
    async with create_app() as app:
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, "0.0.0.0", config.HEALTH_CHECK_PORT)
        await site.start()
        
        logger.info(f"Health check server started on port {config.HEALTH_CHECK_PORT}")
        
        # Keep server running
        try:
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            logger.info("Web server stopped")
        finally:
            await runner.cleanup()

async def main():
    """Main application entry point"""
    logger.info("=" * 50)
    logger.info("TimeToShopping_bot starting up...")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Authorized users: {len(config.AUTHORIZED_USERS)}")
    logger.info("=" * 50)
    
    # Create bot application
    bot_app = BotApplication()
    
    if config.ENVIRONMENT == "production":
        # In production, run both bot and health check server
        async with asyncio.TaskGroup() as tg:
            # Start health check server
            health_task = tg.create_task(start_web_server())
            
            # Start bot polling
            bot_task = tg.create_task(bot_app.start_polling())
    else:
        # In development, run only bot
        await bot_app.start_polling()

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            # Fix for Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)