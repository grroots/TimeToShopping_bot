"""
Logging configuration for TimeToShopping_bot
Configures loguru for structured logging
"""

import sys
from loguru import logger
from config import config  # ИСПРАВЛЕНО: убрал bot.

def setup_logging():
    """Configure logging with loguru"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler for persistent logging
    logger.add(
        config.LOG_FILE,
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Separate file for errors
    logger.add(
        "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logging configuration initialized")
    logger.info(f"Log level: {config.LOG_LEVEL}")
    logger.info(f"Environment: {config.ENVIRONMENT}")

# Initialize logging
setup_logging()

# Export configured logger
__all__ = ["logger"]