"""
Database operations for TimeToShopping_bot
Async database operations using SQLAlchemy
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete, func, and_, desc
from config import config  # ИСПРАВЛЕНО: убрал bot.
from bot.database.models import Base, Post, Analytics, User
from logging_config import logger  # ИСПРАВЛЕНО: убрал bot.

class Database:
    """Database operations manager"""
    
    def __init__(self):
        # Convert sqlite:// to sqlite+aiosqlite:// for async support
        db_url = config.DATABASE_URL
        if db_url.startswith("sqlite:///"):
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        
        self.engine = create_async_engine(
            db_url,
            echo=config.DEBUG,
            future=True
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")
    
    # Post operations
    async def create_post(self, post_data: Dict[str, Any]) -> Post:
        """Create a new post"""
        async with self.async_session() as session:
            post = Post(**post_data)
            session.add(post)
            await session.commit()
            await session.refresh(post)
            logger.info(f"Created post with ID: {post.id}")
            return post
    
    async def get_post(self, post_id: int) -> Optional[Post]:
        """Get post by ID"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Post).options(selectinload(Post.analytics)).where(Post.id == post_id)
            )
            return result.scalar_one_or_none()
    
    async def update_post(self, post_id: int, updates: Dict[str, Any]) -> Optional[Post]:
        """Update post"""
        async with self.async_session() as session:
            updates["updated_at"] = datetime.utcnow()
            await session.execute(
                update(Post).where(Post.id == post_id).values(**updates)
            )
            await session.commit()
            
            # Return updated post
            result = await session.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if post:
                logger.info(f"Updated post ID: {post_id}")
            return post
    
    async def delete_post(self, post_id: int) -> bool:
        """Delete post"""
        async with self.async_session() as session:
            result = await session.execute(delete(Post).where(Post.id == post_id))
            await session.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"Deleted post ID: {post_id}")
            return deleted
    
    async def get_scheduled_posts(self, limit: int = 50) -> List[Post]:
        """Get posts scheduled for publication"""
        async with self.async_session() as session:
            now = datetime.utcnow()
            result = await session.execute(
                select(Post)
                .where(and_(Post.status == "scheduled", Post.publish_at <= now))
                .order_by(Post.publish_at)
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_posts_by_status(self, status: str, limit: int = 20) -> List[Post]:
        """Get posts by status"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Post)
                .where(Post.status == status)
                .order_by(desc(Post.created_at))
                .limit(limit)
            )
            return result.scalars().all()
    
    # Analytics operations
    async def log_analytics(self, post_id: int, action: str, user_id: Optional[str] = None, 
                          extra_data: Optional[str] = None) -> Analytics:  # ИСПРАВЛЕНО: metadata -> extra_data
        """Log analytics event"""
        async with self.async_session() as session:
            analytics = Analytics(
                post_id=post_id,
                action=action,
                user_id=user_id,
                extra_data=extra_data  # ИСПРАВЛЕНО: metadata -> extra_data
            )
            session.add(analytics)
            await session.commit()
            await session.refresh(analytics)
            logger.debug(f"Logged analytics: post_id={post_id}, action={action}")
            return analytics
    
    async def get_post_analytics(self, post_id: int) -> List[Analytics]:
        """Get analytics for specific post"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Analytics)
                .where(Analytics.post_id == post_id)
                .order_by(desc(Analytics.created_at))
            )
            return result.scalars().all()
    
    async def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for specified period"""
        async with self.async_session() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total clicks
            total_clicks = await session.execute(
                select(func.count(Analytics.id))
                .where(and_(Analytics.action == "click_CTA", Analytics.created_at >= start_date))
            )
            
            # Top posts by clicks
            top_posts = await session.execute(
                select(Post.id, Post.title, func.count(Analytics.id).label("clicks"))
                .join(Analytics)
                .where(and_(Analytics.action == "click_CTA", Analytics.created_at >= start_date))
                .group_by(Post.id, Post.title)
                .order_by(desc("clicks"))
                .limit(10)
            )
            
            return {
                "period_days": days,
                "total_clicks": total_clicks.scalar() or 0,
                "top_posts": [
                    {"post_id": row[0], "title": row[1], "clicks": row[2]}
                    for row in top_posts.fetchall()
                ]
            }
    
    # User operations
    async def create_or_update_user(self, telegram_id: int, user_data: Dict[str, Any]) -> User:
        """Create or update user"""
        async with self.async_session() as session:
            # Try to get existing user
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Update existing user
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.last_activity = datetime.utcnow()
            else:
                # Create new user
                user_data["telegram_id"] = telegram_id
                user = User(**user_data)
                session.add(user)
            
            await session.commit()
            await session.refresh(user)
            return user

# Global database instance
db = Database()