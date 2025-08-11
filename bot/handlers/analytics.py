"""
Analytics handlers for TimeToShopping_bot
Handles statistics, reports and data export
"""

import asyncio
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command

from logging_config import logger
from bot.database.db import db
from bot.keyboards.common import get_stats_keyboard, get_back_keyboard

router = Router()

@router.message(Command("stats"))
@router.message(F.text == "📊 Վիճակագրություն")
async def cmd_stats(message: Message):
    """Show statistics menu"""
    await message.answer(
        "📊 <b>Վիճակագրություն</b>\n\n"
        "Ընտրեք ինչ վիճակագրություն եք ուզում տեսնել:",
        reply_markup=get_stats_keyboard()
    )

@router.callback_query(F.data.startswith("stats:"))
async def process_stats_request(callback: CallbackQuery):
    """Process statistics requests"""
    stats_type = callback.data.split(":")[1]
    
    # Show loading message
    loading_msg = await callback.message.edit_text(
        "📊 Բեռնում... Խնդրում ենք սպասել:",
        reply_markup=None
    )
    
    try:
        if stats_type == "day":
            await show_daily_stats(loading_msg)
        elif stats_type == "week":
            await show_weekly_stats(loading_msg)
        elif stats_type == "top":
            await show_top_posts_stats(loading_msg)
        elif stats_type == "formats":
            await show_formats_stats(loading_msg)
        elif stats_type == "export":
            await export_stats_csv(loading_msg)
        else:
            await loading_msg.edit_text(
                "❌ Անհայտ վիճակագրության տեսակ:",
                reply_markup=get_back_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error processing stats request {stats_type}: {e}")
        await loading_msg.edit_text(
            "❌ Չհաջողվեց բեռնել վիճակագրությունը:",
            reply_markup=get_back_keyboard()
        )
    
    await callback.answer()

async def show_daily_stats(message: Message):
    """Show daily statistics"""
    try:
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        
        # Get analytics for today
        analytics_summary = await db.get_analytics_summary(days=1)
        
        # Get published posts today
        from sqlalchemy import select, and_
        from bot.database.models import Post
        
        async with db.async_session() as session:
            result = await session.execute(
                select(Post).where(
                    and_(
                        Post.status == "published",
                        Post.created_at >= start_of_day
                    )
                )
            )
            published_today = result.scalars().all()
        
        # Get scheduled posts for today
        scheduled_today = await db.get_posts_by_status("scheduled", limit=50)
        scheduled_today = [
            p for p in scheduled_today 
            if p.publish_at and p.publish_at.date() == today
        ]
        
        text = f"""
📅 <b>Վիճակագրություն այսօր ({today.strftime('%d.%m.%Y')})</b>

📊 <b>Հիմնական ցուցանիշներ:</b>
• Հրապարակված փոստեր: {len(published_today)}
• Պլանավորված փոստեր: {len(scheduled_today)}
• Ընդամենը կլիկներ: {analytics_summary['total_clicks']}

📈 <b>Ամենաակտիվ փոստերը:</b>
"""
        
        if analytics_summary['top_posts']:
            for i, post in enumerate(analytics_summary['top_posts'][:5], 1):
                title = post['title'][:30] + "..." if len(post['title']) > 30 else post['title']
                text += f"{i}. {title} ({post['clicks']} կլիկ)\n"
        else:
            text += "Այսօր կլիկներ չեն գրանցվել:\n"
        
        await message.edit_text(text, reply_markup=get_back_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing daily stats: {e}")
        raise

async def show_weekly_stats(message: Message):
    """Show weekly statistics"""
    try:
        # Get analytics for last 7 days
        analytics_summary = await db.get_analytics_summary(days=7)
        
        # Get posts created this week
        week_ago = datetime.now() - timedelta(days=7)
        
        async with db.async_session() as session:
            # Published posts this week
            from sqlalchemy import select, and_, func
            from bot.database.models import Post, Analytics
            
            published_result = await session.execute(
                select(func.count(Post.id)).where(
                    and_(
                        Post.status == "published",
                        Post.created_at >= week_ago
                    )
                )
            )
            published_count = published_result.scalar() or 0
            
            # Total posts created this week
            total_result = await session.execute(
                select(func.count(Post.id)).where(
                    Post.created_at >= week_ago
                )
            )
            total_count = total_result.scalar() or 0
            
            # Most active day
            daily_clicks = await session.execute(
                select(
                    func.date(Analytics.created_at).label('date'),
                    func.count(Analytics.id).label('clicks')
                ).where(
                    and_(
                        Analytics.action == "click_CTA",
                        Analytics.created_at >= week_ago
                    )
                ).group_by(func.date(Analytics.created_at))
                .order_by(func.count(Analytics.id).desc())
                .limit(1)
            )
            best_day = daily_clicks.first()
        
        text = f"""
📊 <b>Շաբաթական վիճակագրություն</b>
(Վերջին 7 օր)

📈 <b>Ընդհանուր ցուցանիշներ:</b>
• Ստեղծված փոստեր: {total_count}
• Հրապարակված փոստեր: {published_count}
• Ընդամենը կլիկներ: {analytics_summary['total_clicks']}

🏆 <b>Լավագույն օր:</b>
"""
        
        if best_day:
            text += f"{best_day.date.strftime('%d.%m.%Y')} ({best_day.clicks} կլիկ)\n"
        else:
            text += "Տվյալ չկա:\n"
        
        text += "\n🔝 <b>Ամենաակտիվ փոստերը:</b>\n"
        
        if analytics_summary['top_posts']:
            for i, post in enumerate(analytics_summary['top_posts'][:5], 1):
                title = post['title'][:25] + "..." if len(post['title']) > 25 else post['title']
                text += f"{i}. {title} ({post['clicks']} կլիկ)\n"
        else:
            text += "Կլիկներ չեն գրանցվել:\n"
        
        await message.edit_text(text, reply_markup=get_back_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing weekly stats: {e}")
        raise

async def show_top_posts_stats(message: Message):
    """Show top posts statistics"""
    try:
        # Get top posts of all time
        analytics_summary = await db.get_analytics_summary(days=30)  # Last 30 days
        
        async with db.async_session() as session:
            from sqlalchemy import select, func, desc
            from bot.database.models import Post, Analytics
            
            # Get top posts with click counts
            top_posts_query = await session.execute(
                select(
                    Post.id,
                    Post.title,
                    Post.post_format,
                    Post.created_at,
                    func.count(Analytics.id).label('total_clicks')
                ).select_from(Post)
                .join(Analytics, Post.id == Analytics.post_id)
                .where(Analytics.action == "click_CTA")
                .group_by(Post.id, Post.title, Post.post_format, Post.created_at)
                .order_by(desc('total_clicks'))
                .limit(10)
            )
            
            top_posts = top_posts_query.fetchall()
        
        text = """
🏆 <b>Ամենակարևոր փոստերը</b>
(Ըստ կլիկների քանակի)

"""
        
        if top_posts:
            format_emojis = {
                "selling": "🔥",
                "collection": "📝",
                "info": "💡",
                "promo": "⚡"
            }
            
            for i, post in enumerate(top_posts, 1):
                title = post.title[:30] + "..." if len(post.title) > 30 else post.title
                format_emoji = format_emojis.get(post.post_format, "📄")
                created_date = post.created_at.strftime('%d.%m.%Y') if post.created_at else "?"
                
                text += f"""
{i}. {format_emoji} <b>{title}</b>
   👆 {post.total_clicks} կլիկ | 📅 {created_date}
"""
        else:
            text += "Վիճակագրություն առկա չէ:\n"
        
        await message.edit_text(text, reply_markup=get_back_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing top posts stats: {e}")
        raise

async def show_formats_stats(message: Message):
    """Show statistics by post formats"""
    try:
        async with db.async_session() as session:
            from sqlalchemy import select, func
            from bot.database.models import Post, Analytics
            
            # Get format statistics
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
            
            stats = format_stats.fetchall()
        
        text = """
📈 <b>Վիճակագրություն ֆորմատներով</b>

"""
        
        format_names = {
            "selling": "🔥 Վաճառող փոստ",
            "collection": "📝 Ընտրանի",
            "info": "💡 Տեղեկատվական",
            "promo": "⚡ Ակցիա/Զեղչ",
            None: "📄 Անորոշ"
        }
        
        if stats:
            total_posts = sum(stat.total_posts for stat in stats)
            total_clicks = sum(stat.total_clicks for stat in stats)
            
            for stat in stats:
                format_name = format_names.get(stat.post_format, f"📄 {stat.post_format}")
                posts_percent = (stat.total_posts / total_posts * 100) if total_posts else 0
                clicks_percent = (stat.total_clicks / total_clicks * 100) if total_clicks else 0
                avg_clicks = (stat.total_clicks / stat.published_posts) if stat.published_posts else 0
                
                text += f"""
<b>{format_name}</b>
• Փոստեր: {stat.total_posts} ({posts_percent:.1f}%)
• Հրապարակված: {stat.published_posts}
• Կլիկներ: {stat.total_clicks} ({clicks_percent:.1f}%)
• Միջին կլիկ/փոստ: {avg_clicks:.1f}

"""
        else:
            text += "Վիճակագրություն առկա չէ:\n"
        
        await message.edit_text(text, reply_markup=get_back_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing formats stats: {e}")
        raise

async def export_stats_csv(message: Message):
    """Export statistics to CSV file"""
    try:
        # Create CSV content in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Post ID', 'Title', 'Format', 'Status', 'Created At', 
            'Published At', 'Total Clicks', 'Keywords'
        ])
        
        # Get all posts with analytics
        async with db.async_session() as session:
            from sqlalchemy import select, func, outerjoin
            from bot.database.models import Post, Analytics
            
            posts_with_analytics = await session.execute(
                select(
                    Post.id,
                    Post.title,
                    Post.post_format,
                    Post.status,
                    Post.created_at,
                    Post.publish_at,
                    Post.keywords,
                    func.coalesce(func.count(Analytics.id), 0).label('total_clicks')
                ).select_from(Post)
                .outerjoin(
                    Analytics,
                    and_(Post.id == Analytics.post_id, Analytics.action == 'click_CTA')
                )
                .group_by(
                    Post.id, Post.title, Post.post_format, Post.status,
                    Post.created_at, Post.publish_at, Post.keywords
                )
                .order_by(Post.created_at.desc())
            )
            
            posts = posts_with_analytics.fetchall()
        
        # Write data rows
        for post in posts:
            writer.writerow([
                post.id,
                post.title or "",
                post.post_format or "",
                post.status,
                post.created_at.isoformat() if post.created_at else "",
                post.publish_at.isoformat() if post.publish_at else "",
                post.total_clicks,
                post.keywords or ""
            ])
        
        # Create file buffer
        csv_content = output.getvalue().encode('utf-8-sig')  # UTF-8 with BOM for Excel
        csv_file = BufferedInputFile(csv_content, filename=f"shopping_stats_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
        
        # Send file
        await message.answer_document(
            document=csv_file,
            caption=f"""
📄 <b>Վիճակագրության export</b>

📊 Ընդհանուր:
• Փոստեր: {len(posts)}
• Ամսաթիվ: {datetime.now().strftime('%d.%m.%Y %H:%M')}

CSV ֆայլը կարող եք բացել Excel-ով կամ Google Sheets-ով:
            """,
            reply_markup=get_back_keyboard()
        )
        
        logger.info(f"Stats exported: {len(posts)} posts")
        
    except Exception as e:
        logger.error(f"Error exporting stats: {e}")
        await message.edit_text(
            "❌ Չհաջողվեց export-ը:\n"
            "Խնդրում ենք կրկին փորձել:",
            reply_markup=get_back_keyboard()
        )

# Handle CTA button clicks from channel
@router.callback_query(F.data.startswith("cta_click:"))
async def handle_cta_click(callback: CallbackQuery):
    """Handle CTA button clicks from published posts"""
    try:
        post_id = int(callback.data.split(":")[1])
        user_id = str(callback.from_user.id)
        
        # Log the click
        await db.log_analytics(post_id, "click_CTA", user_id)
        
        # Send acknowledgment
        await callback.answer(
            "✅ Շնորհակալություն հետաքրքրության համար!",
            show_alert=False
        )
        
        logger.info(f"CTA click logged: post_id={post_id}, user_id={user_id}")
        
    except Exception as e:
        logger.error(f"Error handling CTA click: {e}")
        await callback.answer("❌ Տեխնիկական սխալ", show_alert=True)