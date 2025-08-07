"""
Database package for TimeToShopping_bot
SQLAlchemy models and database operations
"""

from .db import db, Database
from .models import Base, Post, Analytics, User

__all__ = ["db", "Database", "Base", "Post", "Analytics", "User"]

# Database configuration constants
DB_CONFIG = {
    "sqlite": {
        "url_template": "sqlite+aiosqlite:///{path}",
        "default_path": "./bot_database.db",
        "pool_size": None,  # Not applicable for SQLite
        "max_overflow": None
    },
    "postgresql": {
        "url_template": "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}",
        "default_port": 5432,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600
    }
}

# Table creation order (for migrations)
TABLE_CREATION_ORDER = [
    "users",      # Independent table
    "posts",      # References users
    "analytics"   # References posts
]

# Database maintenance functions
async def init_database():
    """Initialize database with all tables"""
    await db.init_db()

async def cleanup_database():
    """Close database connections"""
    await db.close()

def get_db_url(db_type: str = "sqlite", **kwargs) -> str:
    """
    Generate database URL for different database types
    
    Args:
        db_type: Type of database (sqlite, postgresql)
        **kwargs: Database connection parameters
        
    Returns:
        Database connection URL
    """
    config = DB_CONFIG.get(db_type)
    if not config:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    if db_type == "sqlite":
        path = kwargs.get("path", config["default_path"])
        return config["url_template"].format(path=path)
    
    elif db_type == "postgresql":
        return config["url_template"].format(
            user=kwargs.get("user", "postgres"),
            password=kwargs.get("password", ""),
            host=kwargs.get("host", "localhost"),
            port=kwargs.get("port", config["default_port"]),
            database=kwargs.get("database", "timetoshopping_bot")
        )

# Data validation utilities
def validate_post_data(post_data: dict) -> tuple[bool, list]:
    """
    Validate post data before database insertion
    
    Args:
        post_data: Dictionary with post data
        
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Required fields
    required_fields = ["text"]
    for field in required_fields:
        if not post_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Text length validation
    text = post_data.get("text", "")
    if len(text) > 4000:  # Telegram message limit
        errors.append("Text too long (max 4000 characters)")
    
    if len(text.strip()) < 10:
        errors.append("Text too short (min 10 characters)")
    
    # Status validation
    valid_statuses = ["draft", "scheduled", "published"]
    status = post_data.get("status", "draft")
    if status not in valid_statuses:
        errors.append(f"Invalid status: {status}")
    
    # Media type validation
    valid_media_types = ["photo", "video", "gif", None]
    media_type = post_data.get("media_type")
    if media_type not in valid_media_types:
        errors.append(f"Invalid media type: {media_type}")
    
    # Format validation
    valid_formats = ["selling", "collection", "info", "promo", None]
    post_format = post_data.get("post_format")
    if post_format not in valid_formats:
        errors.append(f"Invalid post format: {post_format}")
    
    return len(errors) == 0, errors

def validate_analytics_data(analytics_data: dict) -> tuple[bool, list]:
    """
    Validate analytics data before database insertion
    
    Args:
        analytics_data: Dictionary with analytics data
        
    Returns:
        Tuple of (is_valid, errors_list)
    """
    errors = []
    
    # Required fields
    required_fields = ["post_id", "action"]
    for field in required_fields:
        if not analytics_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Post ID validation
    post_id = analytics_data.get("post_id")
    if not isinstance(post_id, int) or post_id <= 0:
        errors.append("Invalid post_id: must be positive integer")
    
    # Action validation
    valid_actions = ["click_CTA", "view", "share", "publish", "edit", "delete"]
    action = analytics_data.get("action")
    if action not in valid_actions:
        errors.append(f"Invalid action: {action}")
    
    return len(errors) == 0, errors

# Database statistics utilities
async def get_database_stats() -> dict:
    """Get database statistics"""
    try:
        async with db.async_session() as session:
            from sqlalchemy import select, func
            
            # Count tables
            posts_count = await session.execute(select(func.count(Post.id)))
            analytics_count = await session.execute(select(func.count(Analytics.id)))
            users_count = await session.execute(select(func.count(User.id)))
            
            return {
                "posts": posts_count.scalar() or 0,
                "analytics": analytics_count.scalar() or 0,
                "users": users_count.scalar() or 0,
                "database_url": str(db.engine.url).replace(db.engine.url.password, "***") if db.engine.url.password else str(db.engine.url)
            }
    except Exception as e:
        return {"error": str(e)}

# Migration utilities
async def check_database_health() -> dict:
    """Check database connectivity and table existence"""
    try:
        async with db.async_session() as session:
            # Check if we can connect
            await session.execute(select(1))
            
            # Check if tables exist
            tables_exist = {}
            for table_name in TABLE_CREATION_ORDER:
                try:
                    if table_name == "posts":
                        await session.execute(select(func.count(Post.id)).limit(1))
                    elif table_name == "analytics":
                        await session.execute(select(func.count(Analytics.id)).limit(1))
                    elif table_name == "users":
                        await session.execute(select(func.count(User.id)).limit(1))
                    tables_exist[table_name] = True
                except Exception:
                    tables_exist[table_name] = False
            
            return {
                "status": "healthy",
                "tables": tables_exist,
                "all_tables_exist": all(tables_exist.values())
            }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }