"""
Scheduler utilities for TimeToShopping_bot
Manages scheduled post publication using APScheduler
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone

from config import config
from logging_config import logger
from bot.database.db import db
from bot.database.models import Post

class SchedulerManager:
    """Manages scheduled tasks for the bot"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=timezone(config.SCHEDULER_TIMEZONE)
        )
        self.bot = None  # Will be set when bot is available
        self.channel_id = config.CHANNEL_CHAT_ID or config.CHANNEL_ID
        
    async def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            
            # Add recurring job to check for scheduled posts
            self.scheduler.add_job(
                self.check_scheduled_posts,
                trigger=IntervalTrigger(minutes=1),  # Check every minute
                id="check_scheduled_posts",
                replace_existing=True
            )
            
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def set_bot(self, bot):
        """Set bot instance for publishing posts"""
        self.bot = bot
        logger.debug("Bot instance set for scheduler")
    
    async def schedule_post(self, post_id: int, publish_at: datetime) -> bool:
        """
        Schedule a post for publication
        
        Args:
            post_id: ID of the post to schedule
            publish_at: When to publish the post
            
        Returns:
            True if scheduled successfully
        """
        try:
            # Update post status in database
            await db.update_post(post_id, {
                "status": "scheduled",
                "publish_at": publish_at
            })
            
            # Add job to scheduler
            job_id = f"publish_post_{post_id}"
            self.scheduler.add_job(
                self.publish_scheduled_post,
                trigger=DateTrigger(run_date=publish_at),
                args=[post_id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Post {post_id} scheduled for {publish_at}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule post {post_id}: {e}")
            return False
    
    async def cancel_scheduled_post(self, post_id: int) -> bool:
        """Cancel a scheduled post"""
        try:
            job_id = f"publish_post_{post_id}"
            
            # Remove job from scheduler
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Job might not exist
            
            # Update post status
            await db.update_post(post_id, {
                "status": "draft",
                "publish_at": None
            })
            
            logger.info(f"Cancelled scheduled post {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel scheduled post {post_id}: {e}")
            return False
    
    async def reschedule_post(self, post_id: int, new_publish_at: datetime) -> bool:
        """Reschedule a post to a new time"""
        try:
            # Cancel existing schedule
            await self.cancel_scheduled_post(post_id)
            
            # Schedule with new time
            return await self.schedule_post(post_id, new_publish_at)
            
        except Exception as e:
            logger.error(f"Failed to reschedule post {post_id}: {e}")
            return False
    
    async def check_scheduled_posts(self):
        """Check for posts that should be published now"""
        try:
            scheduled_posts = await db.get_scheduled_posts(limit=10)
            
            for post in scheduled_posts:
                if post.publish_at and post.publish_at <= datetime.utcnow():
                    await self.publish_scheduled_post(post.id)
                    
        except Exception as e:
            logger.error(f"Error checking scheduled posts: {e}")
    
    async def publish_scheduled_post(self, post_id: int):
        """Publish a scheduled post"""
        try:
            # Get post from database
            post = await db.get_post(post_id)
            if not post:
                logger.error(f"Post {post_id} not found for scheduled publication")
                return
            
            if not self.bot:
                logger.error("Bot instance not available for publishing")
                return
            
            # Publish the post
            success = await self.publish_post_to_channel(post)
            
            if success:
                # Update post status
                await db.update_post(post_id, {"status": "published"})
                
                # Log analytics
                await db.log_analytics(post_id, "publish", metadata="scheduled")
                
                logger.info(f"Successfully published scheduled post {post_id}")
            else:
                logger.error(f"Failed to publish scheduled post {post_id}")
                
                # Reschedule for 5 minutes later
                retry_time = datetime.utcnow() + timedelta(minutes=5)
                await self.schedule_post(post_id, retry_time)
                
        except Exception as e:
            logger.error(f"Error publishing scheduled post {post_id}: {e}")
    
    async def publish_post_to_channel(self, post: Post) -> bool:
        """
        Publish post to Telegram channel
        
        Args:
            post: Post object to publish
            
        Returns:
            True if published successfully
        """
        try:
            if not self.bot:
                logger.error("Bot instance not available")
                return False
            
            # Prepare message text
            message_text = post.text
            
            # Add CTA button if needed
            reply_markup = None
            if "CTA:" in message_text.upper() or any(cta in message_text for cta in ["Գնել", "Փնտրել", "Իմանալ"]):
                from bot.keyboards.common import InlineKeyboardBuilder, InlineKeyboardButton
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(
                        text="🛍️ Փնտրել նմանատիպը",
                        callback_data=f"cta_click:{post.id}"
                    )
                )
                reply_markup = builder.as_markup()
            
            # Send based on media type
            if post.media_type and post.file_id:
                if post.media_type == "photo":
                    await self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=post.file_id,
                        caption=message_text,
                        reply_markup=reply_markup
                    )
                elif post.media_type == "video":
                    await self.bot.send_video(
                        chat_id=self.channel_id,
                        video=post.file_id,
                        caption=message_text,
                        reply_markup=reply_markup
                    )
                elif post.media_type == "gif":
                    await self.bot.send_animation(
                        chat_id=self.channel_id,
                        animation=post.file_id,
                        caption=message_text,
                        reply_markup=reply_markup
                    )
            else:
                # Text only message
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message_text,
                    reply_markup=reply_markup
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish post to channel: {e}")
            return False
    
    async def get_scheduled_posts_info(self) -> List[dict]:
        """Get information about all scheduled posts"""
        try:
            scheduled_posts = await db.get_posts_by_status("scheduled", limit=50)
            
            posts_info = []
            for post in scheduled_posts:
                posts_info.append({
                    "id": post.id,
                    "title": post.title or "Без названия",
                    "format": post.post_format or "unknown",
                    "publish_at": post.publish_at,
                    "created_at": post.created_at
                })
            
            return posts_info
            
        except Exception as e:
            logger.error(f"Error getting scheduled posts info: {e}")
            return []

# Global scheduler manager instance
scheduler_manager = SchedulerManager()