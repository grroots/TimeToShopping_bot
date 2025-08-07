"""
Admin handlers for TimeToShopping_bot
Handles post creation, editing, and management
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command, StateFilter

from bot.logging_config import logger
from bot.database.db import db
from bot.ai.openai_client import openai_client
from bot.keyboards.common import (
    get_main_menu_keyboard, get_post_format_keyboard, get_post_actions_keyboard,
    get_edit_options_keyboard, get_confirmation_keyboard, get_cta_keyboard,
    get_calendar_keyboard, get_time_keyboard, get_media_type_keyboard
)
from bot.utils.scheduler import scheduler_manager

router = Router()

class PostCreationStates(StatesGroup):
    """States for post creation process"""
    choosing_format = State()
    entering_keywords = State()
    entering_details = State()
    reviewing_text = State()
    adding_media = State()
    final_review = State()
    editing_text = State()
    selecting_date = State()
    selecting_time = State()

# Start command
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    welcome_text = """
🎉 Բարի գալուստ TimeToShopping բոտ!

Այս բոտի միջոցով դուք կարող եք:
📝 Ստեղծել նոր փոստեր
🤖 Օգտագործել AI գեներացիա
📊 Դիտել վիճակագրություն
⏰ Պլանավորել հրապարակումներ

Սկսելու համար ընտրեք գործողություն ներքևի մենյուից:
    """
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )

# New post command
@router.message(Command("new_post"))
@router.message(F.text == "📝 Նոր փոստ")
async def cmd_new_post(message: Message, state: FSMContext):
    """Start new post creation"""
    await state.clear()
    await state.set_state(PostCreationStates.choosing_format)
    
    await message.answer(
        "📝 Ստեղծենք նոր փոստ!\n\n"
        "Ի՞նչ ձևաչափի փոստ եք ուզում ստեղծել:",
        reply_markup=get_post_format_keyboard()
    )

# Format selection
@router.callback_query(F.data.startswith("format:"), StateFilter(PostCreationStates.choosing_format))
async def process_format_selection(callback: CallbackQuery, state: FSMContext):
    """Process post format selection"""
    format_type = callback.data.split(":")[1]
    
    await state.update_data(post_format=format_type)
    await state.set_state(PostCreationStates.entering_keywords)
    
    format_names = {
        "selling": "Վաճառող փոստ",
        "collection": "Ընտրանի",
        "info": "Տեղեկատվական փոստ",
        "promo": "Ակցիա/Զեղչ"
    }
    
    format_name = format_names.get(format_type, format_type)
    
    await callback.message.edit_text(
        f"✅ Ձևաչափ՝ {format_name}\n\n"
        "Մուտքագրեք բանալի բառերը կամ գլխավոր թեման:\n"
        "(Օրինակ՝ «ձմեռային կոշիկ, վաճառք, տաք»)"
    )
    
    await callback.answer()

# Keywords input
@router.message(StateFilter(PostCreationStates.entering_keywords))
async def process_keywords_input(message: Message, state: FSMContext):
    """Process keywords input"""
    keywords = message.text.strip()
    
    if len(keywords) < 3:
        await message.answer("❌ Բանալի բառերը չափազանց կարճ են։ Խնդրում ենք մուտքագրել ավելի մանրամասն:")
        return
    
    await state.update_data(keywords=keywords)
    await state.set_state(PostCreationStates.entering_details)
    
    await message.answer(
        "✅ Բանալի բառեր ընդունվեցին\n\n"
        "Կարո՞ղ եք ավելացնել լրացուցիչ մանրամասններ կամ պահանջներ:\n"
        "(Կամ ուղարկեք /skip՝ բաց թողնելու համար)"
    )

# Additional details or skip
@router.message(Command("skip"), StateFilter(PostCreationStates.entering_details))
@router.message(StateFilter(PostCreationStates.entering_details))
async def process_details_input(message: Message, state: FSMContext):
    """Process additional details input"""
    data = await state.get_data()
    
    additional_details = "" if message.text == "/skip" else message.text.strip()
    await state.update_data(additional_details=additional_details)
    
    # Show loading message
    loading_msg = await message.answer("🤖 AI գեներացնում է տեքստը... Խնդրում ենք սպասել:")
    
    try:
        # Generate text using OpenAI
        generated_text = await openai_client.generate_post_text(
            post_format=data["post_format"],
            keywords=data["keywords"],
            additional_details=additional_details
        )
        
        if generated_text:
            await state.update_data(generated_text=generated_text)
            await state.set_state(PostCreationStates.reviewing_text)
            
            await loading_msg.edit_text(
                f"✅ Տեքստը գեներացվեց!\n\n"
                f"📝 <b>Ստացված տեքստ:</b>\n\n"
                f"{generated_text}\n\n"
                f"Ի՞նչ եք ուզում անել:",
                reply_markup=get_text_review_keyboard()
            )
        else:
            await loading_msg.edit_text(
                "❌ Չհաջողվեց գեներացնել տեքստ։ Խնդրում ենք կրկին փորձել:"
            )
            await state.set_state(PostCreationStates.entering_keywords)
            
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        await loading_msg.edit_text(
            "❌ Տեխնիկական սխալ։ Խնդրում ենք կրկին փորձել:"
        )

def get_text_review_keyboard():
    """Get keyboard for text review options"""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Հաստատել", callback_data="text:approve"),
        InlineKeyboardButton(text="✏️ Խմբագրել", callback_data="text:edit")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Վերագեներացնել", callback_data="text:regenerate"),
        InlineKeyboardButton(text="❌ Չեղարկել", callback_data="cancel")
    )
    return builder.as_markup()

# Text review actions
@router.callback_query(F.data.startswith("text:"), StateFilter(PostCreationStates.reviewing_text))
async def process_text_review(callback: CallbackQuery, state: FSMContext):
    """Process text review actions"""
    action = callback.data.split(":")[1]
    data = await state.get_data()
    
    if action == "approve":
        await state.set_state(PostCreationStates.adding_media)
        await callback.message.edit_text(
            "✅ Տեքստը հաստատվեց!\n\n"
            "Ի՞նչ տեսակի մեդիա եք ուզում ավելացնել:",
            reply_markup=get_media_type_keyboard()
        )
        
    elif action == "edit":
        await state.set_state(PostCreationStates.editing_text)
        await callback.message.edit_text(
            f"✏️ Խմբագրեք տեքստը:\n\n"
            f"<b>Ներկայիս տեքստ:</b>\n{data['generated_text']}\n\n"
            f"Ուղարկեք նոր տեքստը:"
        )
        
    elif action == "regenerate":
        loading_msg = await callback.message.edit_text("🔄 Վերագեներացնում... Խնդրում ենք սպասել:")
        
        try:
            new_text = await openai_client.generate_post_text(
                post_format=data["post_format"],
                keywords=data["keywords"],
                additional_details=data.get("additional_details", "")
            )
            
            if new_text:
                await state.update_data(generated_text=new_text)
                await loading_msg.edit_text(
                    f"🔄 Նոր տեքստը գեներացվեց!\n\n"
                    f"📝 <b>Նոր տարբերակ:</b>\n\n"
                    f"{new_text}\n\n"
                    f"Ի՞նչ եք ուզում անել:",
                    reply_markup=get_text_review_keyboard()
                )
            else:
                await loading_msg.edit_text("❌ Չհաջողվեց վերագեներացնել տեքստը:")
        except Exception as e:
            logger.error(f"Error regenerating text: {e}")
            await loading_msg.edit_text("❌ Տեխնիկական սխալ:")
    
    await callback.answer()

# Text editing
@router.message(StateFilter(PostCreationStates.editing_text))
async def process_text_editing(message: Message, state: FSMContext):
    """Process manual text editing"""
    new_text = message.text.strip()
    
    if len(new_text) < 10:
        await message.answer("❌ Տեքստը չափազանց կարճ է։ Խնդրում ենք մուտքագրել ավելի երկար տեքստ:")
        return
    
    await state.update_data(generated_text=new_text)
    await state.set_state(PostCreationStates.adding_media)
    
    await message.answer(
        "✅ Տեքստը թարմացվեց!\n\n"
        "Ի՞նչ տեսակի մեդիա եք ուզում ավելացնել:",
        reply_markup=get_media_type_keyboard()
    )

# Media type selection
@router.callback_query(F.data.startswith("media:"), StateFilter(PostCreationStates.adding_media))
async def process_media_selection(callback: CallbackQuery, state: FSMContext):
    """Process media type selection"""
    media_type = callback.data.split(":")[1]
    
    if media_type == "none":
        await state.update_data(media_type=None, file_id=None)
        await finalize_post_creation(callback, state)
    else:
        await state.update_data(media_type=media_type)
        
        media_instructions = {
            "photo": "🖼️ Ուղարկեք նկարը:",
            "video": "🎥 Ուղարկեք վիդեոն:",
            "gif": "🎞️ Ուղարկեք GIF-ը:"
        }
        
        instruction = media_instructions.get(media_type, "Ուղարկեք ֆայլը:")
        await callback.message.edit_text(instruction)
    
    await callback.answer()

# Media upload handling
@router.message(F.content_type.in_([ContentType.PHOTO, ContentType.VIDEO, ContentType.ANIMATION]), 
                StateFilter(PostCreationStates.adding_media))
async def process_media_upload(message: Message, state: FSMContext):
    """Process media upload"""
    data = await state.get_data()
    expected_media_type = data.get("media_type")
    
    # Get file_id based on media type
    file_id = None
    actual_media_type = None
    
    if message.photo and expected_media_type == "photo":
        file_id = message.photo[-1].file_id  # Get largest photo size
        actual_media_type = "photo"
    elif message.video and expected_media_type == "video":
        file_id = message.video.file_id
        actual_media_type = "video"
    elif message.animation and expected_media_type == "gif":
        file_id = message.animation.file_id
        actual_media_type = "gif"
    else:
        await message.answer(
            f"❌ Սխալ մեդիա տեսակ։ Ակնկալվում էր {expected_media_type}։"
        )
        return
    
    await state.update_data(file_id=file_id, media_type=actual_media_type)
    await finalize_post_creation(message, state)

async def finalize_post_creation(event, state: FSMContext):
    """Finalize post creation and show preview"""
    data = await state.get_data()
    
    try:
        # Create post in database
        post_data = {
            "title": data.get("keywords", "")[:100],  # Use keywords as title
            "keywords": data.get("keywords", ""),
            "text": data.get("generated_text", ""),
            "media_type": data.get("media_type"),
            "file_id": data.get("file_id"),
            "status": "draft",
            "post_format": data.get("post_format"),
            "created_by": event.from_user.id if hasattr(event, 'from_user') else None
        }
        
        post = await db.create_post(post_data)
        
        await state.clear()
        await state.set_state(PostCreationStates.final_review)
        await state.update_data(post_id=post.id)
        
        # Show post preview
        await show_post_preview(event, post)
        
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        if hasattr(event, 'answer'):
            await event.answer("❌ Չհաջողվեց ստեղծել փոստը:")
        else:
            await event.message.answer("❌ Չհաջողվեց ստեղծել փոստը:")

async def show_post_preview(event, post):
    """Show post preview with actions"""
    preview_text = f"📋 <b>Փոստի նախադիտում:</b>\n\n{post.text}"
    
    # Send preview based on media type
    if post.media_type and post.file_id:
        if post.media_type == "photo":
            await event.message.answer_photo(
                photo=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            ) if hasattr(event, 'message') else await event.answer_photo(
                photo=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            )
        elif post.media_type == "video":
            await event.message.answer_video(
                video=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            ) if hasattr(event, 'message') else await event.answer_video(
                video=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            )
        elif post.media_type == "gif":
            await event.message.answer_animation(
                animation=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            ) if hasattr(event, 'message') else await event.answer_animation(
                animation=post.file_id,
                caption=preview_text,
                reply_markup=get_post_actions_keyboard(post.id, post.status)
            )
    else:
        # Text only
        if hasattr(event, 'message'):
            await event.message.answer(preview_text, reply_markup=get_post_actions_keyboard(post.id, post.status))
        else:
            await event.answer(preview_text, reply_markup=get_post_actions_keyboard(post.id, post.status))

# Cancel action
@router.callback_query(F.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Գործողությունը չեղարկվեց:",
        reply_markup=None
    )
    
    # Show main menu
    await callback.message.answer(
        "Ընտրեք նոր գործողություն:",
        reply_markup=get_main_menu_keyboard()
    )
    
    await callback.answer()

# Post actions handling
@router.callback_query(F.data.startswith("publish:"))
async def process_publish_post(callback: CallbackQuery, state: FSMContext):
    """Handle post publication"""
    post_id = int(callback.data.split(":")[1])
    
    try:
        post = await db.get_post(post_id)
        if not post:
            await callback.answer("❌ Փոստը չի գտնվել:", show_alert=True)
            return
        
        # Set bot instance for scheduler
        scheduler_manager.set_bot(callback.bot)
        
        # Publish immediately
        success = await scheduler_manager.publish_post_to_channel(post)
        
        if success:
            # Update post status
            await db.update_post(post_id, {"status": "published"})
            await db.log_analytics(post_id, "publish", str(callback.from_user.id))
            
            await callback.message.edit_text(
                "✅ Փոստը հրապարակվեց հաջողությամբ!",
                reply_markup=None
            )
            
            logger.info(f"Post {post_id} published by user {callback.from_user.id}")
        else:
            await callback.answer("❌ Չհաջողվեց հրապարակել փոստը:", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error publishing post {post_id}: {e}")
        await callback.answer("❌ Տեխնիկական սխալ:", show_alert=True)

@router.callback_query(F.data.startswith("schedule:"))
async def process_schedule_post(callback: CallbackQuery, state: FSMContext):
    """Handle post scheduling"""
    post_id = int(callback.data.split(":")[1])
    
    await state.update_data(scheduling_post_id=post_id)
    await state.set_state(PostCreationStates.selecting_date)
    
    # Show calendar
    now = datetime.now()
    await callback.message.edit_text(
        "📅 Ընտրեք հրապարակման ամսաթիվը:",
        reply_markup=get_calendar_keyboard(now.year, now.month)
    )

@router.callback_query(F.data.startswith("cal_select:"))
async def process_date_selection(callback: CallbackQuery, state: FSMContext):
    """Handle calendar date selection"""
    _, year, month, day = callback.data.split(":")
    selected_date = datetime(int(year), int(month), int(day))
    
    # Check if date is not in the past
    if selected_date.date() < datetime.now().date():
        await callback.answer("❌ Չեք կարող ընտրել անցած ամսաթիվ:", show_alert=True)
        return
    
    await state.update_data(selected_date=selected_date)
    await state.set_state(PostCreationStates.selecting_time)
    
    await callback.message.edit_text(
        f"📅 Ընտրված ամսաթիվ: {selected_date.strftime('%d.%m.%Y')}\n\n"
        f"🕒 Ընտրեք ժամը:",
        reply_markup=get_time_keyboard()
    )

@router.callback_query(F.data.startswith("time:"))
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    """Handle time selection"""
    time_str = callback.data.split(":", 1)[1]
    
    if time_str == "custom":
        await callback.message.edit_text(
            "🕒 Մուտքագրեք ժամը HH:MM ձևաչափով (օր.՝ 14:30):"
        )
        return
    
    try:
        data = await state.get_data()
        selected_date = data["selected_date"]
        
        # Parse time
        hour, minute = map(int, time_str.split(":"))
        publish_datetime = selected_date.replace(hour=hour, minute=minute)
        
        # Check if datetime is not in the past
        if publish_datetime <= datetime.now():
            await callback.answer("❌ Ընտրված ժամը անցել է:", show_alert=True)
            return
        
        # Schedule the post
        post_id = data["scheduling_post_id"]
        success = await scheduler_manager.schedule_post(post_id, publish_datetime)
        
        if success:
            await callback.message.edit_text(
                f"✅ Փոստը պլանավորվեց!\n\n"
                f"📅 Հրապարակման ժամ: {publish_datetime.strftime('%d.%m.%Y %H:%M')}"
            )
            await state.clear()
        else:
            await callback.answer("❌ Չհաջողվեց պլանավորել փոստը:", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        await callback.answer("❌ Տեխնիկական սխալ:", show_alert=True)

@router.callback_query(F.data.startswith("delete:"))
async def process_delete_post(callback: CallbackQuery, state: FSMContext):
    """Handle post deletion"""
    post_id = int(callback.data.split(":")[1])
    
    await callback.message.edit_text(
        "⚠️ Վստա՞հ եք, որ ուզում եք ջնջել այս փոստը:",
        reply_markup=get_confirmation_keyboard("delete", post_id)
    )

@router.callback_query(F.data.startswith("confirm_delete:"))
async def process_confirm_delete(callback: CallbackQuery, state: FSMContext):
    """Confirm post deletion"""
    post_id = int(callback.data.split(":")[1])
    
    try:
        # Cancel scheduled job if exists
        await scheduler_manager.cancel_scheduled_post(post_id)
        
        # Delete from database
        success = await db.delete_post(post_id)
        
        if success:
            await callback.message.edit_text("✅ Փոստը ջնջվեց հաջողությամբ:")
            logger.info(f"Post {post_id} deleted by user {callback.from_user.id}")
        else:
            await callback.answer("❌ Չհաջողվեց ջնջել փոստը:", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}")
        await callback.answer("❌ Տեխնիկական սխալ:", show_alert=True)

# Drafts command
@router.message(Command("drafts"))
@router.message(F.text == "📋 Նախագծեր")
async def cmd_show_drafts(message: Message):
    """Show draft posts"""
    try:
        drafts = await db.get_posts_by_status("draft", limit=10)
        
        if not drafts:
            await message.answer("📋 Նախագծեր չկան:")
            return
        
        text = "📋 <b>Նախագծերի ցանկը:</b>\n\n"
        
        for i, post in enumerate(drafts, 1):
            title = post.title or post.keywords[:30] if post.keywords else "Անանուն"
            created = post.created_at.strftime("%d.%m %H:%M") if post.created_at else "?"
            text += f"{i}. {title}... (📅 {created})\n"
        
        await message.answer(text)
        
        # Show first draft for quick access
        if drafts:
            await show_post_preview(message, drafts[0])
            
    except Exception as e:
        logger.error(f"Error showing drafts: {e}")
        await message.answer("❌ Չհաջողվեց բեռնել նախագծերը:")

# Scheduled posts command
@router.message(Command("scheduled"))
@router.message(F.text == "⏰ Պլանավորված")
async def cmd_show_scheduled(message: Message):
    """Show scheduled posts"""
    try:
        scheduled_posts = await scheduler_manager.get_scheduled_posts_info()
        
        if not scheduled_posts:
            await message.answer("⏰ Պլանավորված փոստեր չկան:")
            return
        
        text = "⏰ <b>Պլանավորված փոստեր:</b>\n\n"
        
        for i, post_info in enumerate(scheduled_posts, 1):
            title = post_info["title"][:30] + "..." if len(post_info["title"]) > 30 else post_info["title"]
            publish_time = post_info["publish_at"].strftime("%d.%m %H:%M") if post_info["publish_at"] else "?"
            text += f"{i}. {title}\n   📅 {publish_time}\n\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error showing scheduled posts: {e}")
        await message.answer("❌ Չհաջողվեց բեռնել պլանավորված փոստերը:")

# Help command
@router.message(Command("help"))
@router.message(F.text == "ℹ️ Օգնություն")
async def cmd_help(message: Message):
    """Show help information"""
    help_text = """
📚 <b>Օգնություն - TimeToShopping Bot</b>

<b>Հիմնական հրամաններ:</b>
📝 /new_post - Նոր փոստ ստեղծել
📋 /drafts - Նախագծերը դիտել
⏰ /scheduled - Պլանավորված փոստերը դիտել
📊 /stats - Վիճակագրություն

<b>Փոստի ստեղծման քայլեր:</b>
1️⃣ Ընտրել ձևաչափը (վաճառող, ընտրանի, տեղեկատվական, ակցիա)
2️⃣ Մուտքագրել բանալի բառերը
3️⃣ Ավելացնել լրացուցիչ մանրամասներ (ոչ պարտադիր)
4️⃣ AI-ը կգեներացնի տեքստը
5️⃣ Ավելացնել մեդիա (նկար/վիդեո/GIF)
6️⃣ Հրապարակել կամ պլանավորել

<b>Ձևաչափների նկարագրություն:</b>
🔥 Վաճառող - գործելու կոչ և արագ վաճառք
📝 Ընտրանի - ապրանքների ցանկ էմոջիներով
💡 Տեղեկատվական - օգտակար խորհուրդներ և տեղեկություններ
⚡ Ակցիա - զեղչեր և հատուկ առաջարկություններ

Այլ հարցերի դեպքում դիմեք ադմինիստրատորին:
    """
    
    await message.answer(help_text)

# Back to main menu
@router.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Go back to main menu"""
    await state.clear()
    
    await callback.message.edit_text(
        "🏠 Գլխավոր մենյու\n\nԸնտրեք գործողություն:",
        reply_markup=None
    )
    
    await callback.message.answer(
        "Ընտրեք գործողություն:",
        reply_markup=get_main_menu_keyboard()
    )
    
    await callback.answer()