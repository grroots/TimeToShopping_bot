"""
CSV Export utilities for TimeToShopping_bot
Export analytics and posts data to CSV format
"""

import csv
import io
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from aiogram.types import BufferedInputFile

from bot.database.db import db
from logging_config import logger

class CSVExporter:
    """CSV export functionality for analytics and posts"""
    
    def __init__(self):
        self.encoding = 'utf-8-sig'  # UTF-8 with BOM for Excel compatibility
    
    async def export_posts_data(self, status: Optional[str] = None, limit: int = 1000) -> BufferedInputFile:
        """
        Export posts data to CSV
        
        Args:
            status: Filter by post status (optional)
            limit: Maximum number of posts to export
            
        Returns:
            BufferedInputFile ready for sending
        """
        try:
            # Get posts data
            if status:
                posts = await db.get_posts_by_status(status, limit)
            else:
                # Get all posts with analytics
                posts = await self._get_all_posts_with_analytics(limit)
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = [
                'Post ID', 'Title', 'Format', 'Status', 'Created At', 'Published At',
                'Keywords', 'Text Preview', 'Media Type', 'Total Clicks', 'Total Views'
            ]
            writer.writerow(headers)
            
            # Data rows
            for post in posts:
                # Get analytics for this post
                analytics = await db.get_post_analytics(post.id)
                clicks = len([a for a in analytics if a.action == 'click_CTA'])
                views = len([a for a in analytics if a.action == 'view'])
                
                # Text preview (first 100 characters)
                text_preview = post.text[:100] + "..." if len(post.text) > 100 else post.text
                text_preview = text_preview.replace('\n', ' ').replace('\r', ' ')
                
                row = [
                    post.id,
                    post.title or "",
                    post.post_format or "",
                    post.status,
                    post.created_at.isoformat() if post.created_at else "",
                    post.publish_at.isoformat() if post.publish_at else "",
                    post.keywords or "",
                    text_preview,
                    post.media_type or "",
                    clicks,
                    views
                ]
                writer.writerow(row)
            
            # Create file
            csv_content = output.getvalue().encode(self.encoding)
            filename = f"posts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return BufferedInputFile(csv_content, filename=filename)
            
        except Exception as e:
            logger.error(f"Error exporting posts data: {e}")
            raise
    
    async def export_analytics_data(self, days: int = 30) -> BufferedInputFile:
        """
        Export analytics data to CSV
        
        Args:
            days: Number of days to include in export
            
        Returns:
            BufferedInputFile ready for sending
        """
        try:
            # Get analytics data for the period
            start_date = datetime.utcnow() - timedelta(days=days)
            
            async with db.async_session() as session:
                from sqlalchemy import select, and_
                from bot.database.models import Analytics, Post
                
                result = await session.execute(
                    select(Analytics, Post.title, Post.post_format)
                    .join(Post, Analytics.post_id == Post.id)
                    .where(Analytics.created_at >= start_date)
                    .order_by(Analytics.created_at.desc())
                )
                
                analytics_data = result.fetchall()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            headers = [
                'Analytics ID', 'Post ID', 'Post Title', 'Post Format', 'Action',
                'User ID', 'Timestamp', 'Metadata'
            ]
            writer.writerow(headers)
            
            # Data rows
            for analytics, post_title, post_format in analytics_data:
                row = [
                    analytics.id,
                    analytics.post_id,
                    post_title or "Unknown",
                    post_format or "",
                    analytics.action,
                    analytics.user_id or "",
                    analytics.created_at.isoformat() if analytics.created_at else "",
                    analytics.metadata or ""
                ]
                writer.writerow(row)
            
            # Create file
            csv_content = output.getvalue().encode(self.encoding)
            filename = f"analytics_export_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return BufferedInputFile(csv_content, filename=filename)
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            raise
    
    async def export_summary_report(self, days: int = 30) -> BufferedInputFile:
        """
        Export summary report with key metrics
        
        Args:
            days: Number of days to include in report
            
        Returns:
            BufferedInputFile ready for sending
        """
        try:
            # Get summary data
            analytics_summary = await db.get_analytics_summary(days)
            
            # Get format statistics
            async with db.async_session() as session:
                from sqlalchemy import select, func, and_
                from bot.database.models import Post, Analytics
                
                # Format performance
                format_stats = await session.execute(
                    select(
                        Post.post_format,
                        func.count(Post.id).label('total_posts'),
                        func.count(
                            func.case([(Post.status == 'published', 1)], else_=None)
                        ).label('published_posts'),
                        func.coalesce(func.count(Analytics.id), 0).label('total_clicks')
                    ).select_from(Post)
                    .outerjoin(
                        Analytics, 
                        and_(Post.id == Analytics.post_id, Analytics.action == 'click_CTA')
                    )
                    .group_by(Post.post_format)
                    .order_by(func.count(Post.id).desc())
                )
                
                format_data = format_stats.fetchall()
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Summary section
            writer.writerow(['SUMMARY REPORT'])
            writer.writerow(['Report Period', f'{days} days'])
            writer.writerow(['Generated At', datetime.now().isoformat()])
            writer.writerow([])
            
            # Overall metrics
            writer.writerow(['OVERALL METRICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Clicks', analytics_summary['total_clicks']])
            writer.writerow(['Top Performing Posts', len(analytics_summary['top_posts'])])
            writer.writerow([])
            
            # Top posts
            writer.writerow(['TOP PERFORMING POSTS'])
            writer.writerow(['Rank', 'Post ID', 'Title', 'Clicks'])
            for i, post in enumerate(analytics_summary['top_posts'][:10], 1):
                title = post['title'][:50] + "..." if len(post['title']) > 50 else post['title']
                writer.writerow([i, post['post_id'], title, post['clicks']])
            writer.writerow([])
            
            # Format statistics
            writer.writerow(['FORMAT STATISTICS'])
            writer.writerow(['Format', 'Total Posts', 'Published Posts', 'Total Clicks', 'Avg Clicks/Post'])
            
            for stat in format_data:
                format_name = stat.post_format or 'Unknown'
                avg_clicks = (stat.total_clicks / stat.published_posts) if stat.published_posts > 0 else 0
                writer.writerow([
                    format_name,
                    stat.total_posts,
                    stat.published_posts,
                    stat.total_clicks,
                    f"{avg_clicks:.2f}"
                ])
            
            # Create file
            csv_content = output.getvalue().encode(self.encoding)
            filename = f"summary_report_{days}days_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return BufferedInputFile(csv_content, filename=filename)
            
        except Exception as e:
            logger.error(f"Error exporting summary report: {e}")
            raise
    
    async def _get_all_posts_with_analytics(self, limit: int) -> List:
        """Get all posts with their analytics data"""
        async with db.async_session() as session:
            from sqlalchemy import select
            from bot.database.models import Post
            
            result = await session.execute(
                select(Post)
                .order_by(Post.created_at.desc())
                .limit(limit)
            )
            
            return result.scalars().all()

# Convenience functions for direct use

async def export_posts_to_csv(status: Optional[str] = None, limit: int = 1000) -> BufferedInputFile:
    """
    Export posts to CSV file
    
    Args:
        status: Optional status filter
        limit: Maximum number of posts
        
    Returns:
        BufferedInputFile ready for Telegram
    """
    exporter = CSVExporter()
    return await exporter.export_posts_data(status, limit)

async def export_analytics_to_csv(days: int = 30) -> BufferedInputFile:
    """
    Export analytics to CSV file
    
    Args:
        days: Number of days to include
        
    Returns:
        BufferedInputFile ready for Telegram
    """
    exporter = CSVExporter()
    return await exporter.export_analytics_data(days)

async def export_summary_to_csv(days: int = 30) -> BufferedInputFile:
    """
    Export summary report to CSV file
    
    Args:
        days: Number of days to include
        
    Returns:
        BufferedInputFile ready for Telegram
    """
    exporter = CSVExporter()
    return await exporter.export_summary_report(days)

# JSON export functionality

async def export_posts_to_json(status: Optional[str] = None, limit: int = 1000) -> BufferedInputFile:
    """Export posts data to JSON format"""
    try:
        if status:
            posts = await db.get_posts_by_status(status, limit)
        else:
            exporter = CSVExporter()
            posts = await exporter._get_all_posts_with_analytics(limit)
        
        # Convert posts to JSON-serializable format
        posts_data = []
        for post in posts:
            # Get analytics
            analytics = await db.get_post_analytics(post.id)
            clicks = len([a for a in analytics if a.action == 'click_CTA'])
            views = len([a for a in analytics if a.action == 'view'])
            
            post_dict = post.to_dict()
            post_dict['analytics'] = {
                'total_clicks': clicks,
                'total_views': views,
                'engagement_rate': (clicks / views * 100) if views > 0 else 0
            }
            posts_data.append(post_dict)
        
        # Create JSON content
        json_content = json.dumps(posts_data, ensure_ascii=False, indent=2, default=str)
        json_bytes = json_content.encode('utf-8')
        
        filename = f"posts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return BufferedInputFile(json_bytes, filename=filename)
        
    except Exception as e:
        logger.error(f"Error exporting posts to JSON: {e}")
        raise