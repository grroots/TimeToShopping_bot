"""
Scheduler handlers for TimeToShopping_bot
Handles scheduled post management and calendar operations
"""

from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from logging_config import logger
from bot.database.db import db
from bot.utils.scheduler import scheduler_manager
from bot.keyboards.common import get_calendar_keyboard, get_time_keyboard, get_back_keyboard

router = Router()

@router.callback_query(F.data.startswith("cal_prev:"))
async def process_calendar_prev(callback: CallbackQuery):
    """Handle calendar previous month navigation"""
    try:
        _, year, month = callback.data.split(":")
        year, month = int(year), int(month)
        
        # Calculate previous month
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
        
        await callback.message.edit_reply_markup(
            reply_markup=get_calendar_keyboard(prev_year, prev_month)
        )
        
    except Exception as e:
        logger.error(f"Error navigating calendar: {e}")
        await callback.answer("❌ Օրացույցի սխալ", show_alert=True)

@router.callback_query(F.data.startswith("cal_next:"))
async def process_calendar_next(callback: CallbackQuery):
    """Handle calendar next month navigation"""
    try:
        _, year, month = callback.data.split(":")
        year, month = int(year), int(month)
        
        # Calculate next month
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        
        await callback.message.edit_reply_markup(
            reply_markup=get_calendar_keyboard(next_year, next_month)
        )
        
    except Exception as e:
        logger.error(f"Error navigating calendar: {e}")
        await callback.answer("❌ Օրացույցի սխալ", show_alert=True)

@router.callback_query(F.data == "ignore")
async def process_ignore_callback(callback: CallbackQuery):
    """Ignore calendar header clicks"""
    await callback.answer()

@router.callback_query(F.data.startswith("reschedule:"))
async def process_reschedule_post(callback: CallbackQuery, state: FSMContext):
    """Handle post rescheduling"""
    try:
        post_id = int(callback.data.split(":")[1])
        
        # Get current post info
        post = await db.get_post(post_id)
        if not post:
            await callback.answer("❌ Փոստը չի գտնվել", show_alert=True)
            return
        
        current_time = post.publish_at.strftime('%d.%m.%Y %H:%M') if post.publish_at else "անհայտ"
        
        await state.update_data(scheduling_post_id=post_id, action="reschedule")
        
        # Show calendar for new date selection
        now = datetime.now()
        await callback.message.edit_text(
            f"🕒 <b>Փոստի վերապլանավորում</b>\n\n"
            f"Ներկայիս ժամ: {current_time}\n\n"
            f"📅 Ընտրեք նոր ամսաթիվը:",
            reply_markup=get_calendar_keyboard(now.year, now.month)
        )
        
    except Exception as e:
        logger.error(f"Error starting reschedule: {e}")
        await callback.answer("❌ Տեխնիկական սխալ", show_alert=True)

@router.callback_query(F.data.startswith("publish_now:"))
async def process_publish_now(callback: CallbackQuery):
    """Handle immediate publication of scheduled post"""
    try:
        post_id = int(callback.data.split(":")[1])
        
        # Get post
        post = await db.get_post(post_id)
        if not post:
            await callback.answer("❌ Փոստը չի գտնվել", show_alert=True)
            return
        
        # Set bot for scheduler
        scheduler_manager.set_bot(callback.bot)
        
        # Cancel scheduled job
        await scheduler_manager.cancel_scheduled_post(post_id)
        
        # Publish immediately
        success = await scheduler_manager.publish_post_to_channel(post)
        
        if success:
            await db.update_post(post_id, {"status": "published"})
            await db.log_analytics(post_id, "publish", str(callback.from_user.id), "manual_publish")
            
            await callback.message.edit_text(
                "✅ Փոստը հրապարակվեց հաջողությամբ!",
                reply_markup=None
            )
            
            logger.info(f"Scheduled post {post_id} published immediately by user {callback.from_user.id}")
        else:
            await callback.answer("❌ Չհաջողվեց հրապարակել փոստը", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error publishing scheduled post immediately: {e}")
        await callback.answer("❌ Տեխնիկական սխալ", show_alert=True)

@router.message(Command("scheduler_status"))
async def cmd_scheduler_status(message: Message):
    """Show scheduler status and jobs"""
    try:
        # Get scheduled posts info
        scheduled_posts = await scheduler_manager.get_scheduled_posts_info()
        
        # Get scheduler status
        is_running = scheduler_manager.scheduler.running if scheduler_manager.scheduler else False
        
        text = f"""
🤖 <b>Պլանավորիչի կարգավիճակ</b>

📊 <b>Ընդհանուր տվյալներ:</b>
• Կարգավիճակ: {'🟢 Աշխատում է' if is_running else '🔴 Կանգնած է'}
• Պլանավորված փոստեր: {len(scheduled_posts)}

⏰ <b>Մոտակա հրապարակումներ:</b>
"""
        
        if scheduled_posts:
            # Sort by publish time
            sorted_posts = sorted(
                [p for p in scheduled_posts if p['publish_at']], 
                key=lambda x: x['publish_at']
            )
            
            for post in sorted_posts[:5]:  # Show next 5 posts
                title = post['title'][:25] + "..." if len(post['title']) > 25 else post['title']
                time_str = post['publish_at'].strftime('%d.%m.%Y %H:%M')
                time_left = post['publish_at'] - datetime.now()
                
                if time_left.total_seconds() > 0:
                    if time_left.days > 0:
                        time_left_str = f"{time_left.days} օր"
                    elif time_left.seconds > 3600:
                        hours = time_left.seconds // 3600
                        time_left_str = f"{hours} ժամ"
                    else:
                        minutes = time_left.seconds // 60
                        time_left_str = f"{minutes} րոպե"
                else:
                    time_left_str = "ակնկալում"
                
                text += f"• {title} - {time_str} ({time_left_str})\n"
        else:
            text += "Պլանավորված փոստեր չկան\n"
        
        await message.answer(text, reply_markup=get_back_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing scheduler status: {e}")
        await message.answer("❌ Չհաջողվեց բեռնել պլանավորիչի տվյալները")

@router.message(Command("clear_failed"))
async def cmd_clear_failed_jobs(message: Message):
    """Clear failed scheduled jobs"""
    try:
        # Get posts that should have been published but failed
        failed_posts = []
        
        async with db.async_session() as session:
            from sqlalchemy import select, and_
            from bot.database.models import Post
            
            now = datetime.now()
            result = await session.execute(
                select(Post).where(
                    and_(
                        Post.status == "scheduled",
                        Post.publish_at < now - timedelta(minutes=10)  # 10+ minutes overdue
                    )
                )
            )
            failed_posts = result.scalars().all()
        
        if not failed_posts:
            await message.answer("✅ Ձախողված պլանավորված փոստեր չկան")
            return
        
        # Reset failed posts to draft status
        for post in failed_posts:
            await db.update_post(post.id, {
                "status": "draft", 
                "publish_at": None
            })
            
            # Remove from scheduler if exists
            try:
                job_id = f"publish_post_{post.id}"
                scheduler_manager.scheduler.remove_job(job_id)
            except:
                pass  # Job might not exist
        
        await message.answer(
            f"🧹 Մաքրվեց {len(failed_posts)} ձախողված փոստ։\n"
            f"Դրանք վերադարձվեցին նախագիծ կարգավիճակի։"
        )
        
        logger.info(f"Cleared {len(failed_posts)} failed scheduled posts")
        
    except Exception as e:
        logger.error(f"Error clearing failed jobs: {e}")
        await message.answer("❌ Չհաջողվեց մաքրել ձախողված փոստերը")

@router.callback_query(F.data == "scheduler:restart")
async def process_restart_scheduler(callback: CallbackQuery):
    """Restart scheduler (admin only)"""
    try:
        # Stop and start scheduler
        await scheduler_manager.stop()
        await scheduler_manager.start()
        
        await callback.message.edit_text(
            "🔄 Պլանավորիչը վերագործարկվեց հաջողությամբ!",
            reply_markup=get_back_keyboard()
        )
        
        logger.info(f"Scheduler restarted by user {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error restarting scheduler: {e}")
        await callback.answer("❌ Չհաջողվեց վերագործարկել", show_alert=True)

# Debug command for testing scheduled posts
@router.message(Command("test_schedule"))
async def cmd_test_schedule(message: Message):
    """Test scheduling functionality (creates a test post in 2 minutes)"""
    try:
        # Create a test post
        test_post_data = {
            "title": "Test փոստ",
            "keywords": "test, ստուգում",
            "text": "🧪 Սա ստուգման փոստ է։ Եթե տեսնում եք սա, ապա պլանավորիչը աշխատում է։",
            "status": "draft",
            "post_format": "info",
            "created_by": message.from_user.id
        }
        
        post = await db.create_post(test_post_data)
        
        # Schedule for 2 minutes from now
        schedule_time = datetime.now() + timedelta(minutes=2)
        success = await scheduler_manager.schedule_post(post.id, schedule_time)
        
        if success:
            await message.answer(
                f"🧪 <b>Ստուգման փոստ ստեղծվեց!</b>\n\n"
                f"📅 Պլանավորված ժամ: {schedule_time.strftime('%H:%M:%S')}\n"
                f"⏰ 2 րոպե հետո տեսեք կհրապարակվի:\n\n"
                f"Post ID: {post.id}"
            )
        else:
            await message.answer("❌ Չհաջողվեց պլանավորել ստուգման փոստը")
            
    except Exception as e:
        logger.error(f"Error creating test scheduled post: {e}")
        await message.answer("❌ Ստուգման փոստի ստեղծման սխալ")

@router.message(Command("next_scheduled"))
async def cmd_next_scheduled(message: Message):
    """Show next scheduled post details"""
    try:
        scheduled_posts = await scheduler_manager.get_scheduled_posts_info()
        
        if not scheduled_posts:
            await message.answer("⏰ Պլանավորված փոստեր չկան")
            return
        
        # Find next post to be published
        now = datetime.now()
        upcoming_posts = [
            p for p in scheduled_posts 
            if p['publish_at'] and p['publish_at'] > now
        ]
        
        if not upcoming_posts:
            await message.answer("📅 Մոտակա պլանավորված փոստեր չկան")
            return
        
        # Sort by publish time and get the next one
        next_post = min(upcoming_posts, key=lambda x: x['publish_at'])
        
        time_left = next_post['publish_at'] - now
        
        if time_left.days > 0:
            time_str = f"{time_left.days} օր, {time_left.seconds // 3600} ժամ"
        elif time_left.seconds > 3600:
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            time_str = f"{hours} ժամ, {minutes} րոպե"
        else:
            minutes = time_left.seconds // 60
            time_str = f"{minutes} րոպե"
        
        text = f"""
⏰ <b>Հաջորդ պլանավորված փոստ</b>

📝 <b>Վերնագիր:</b> {next_post['title']}
📅 <b>Ամսաթիվ:</b> {next_post['publish_at'].strftime('%d.%m.%Y %H:%M')}
⏳ <b>Մնացած ժամանակ:</b> {time_str}
🏷️ <b>Ձևաչափ:</b> {next_post.get('format', 'անհայտ')}

📊 Post ID: {next_post['id']}
        """
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error showing next scheduled post: {e}")
        await message.answer("❌ Չհաջողվեց գտնել հաջորդ պլանավորված փոստը")