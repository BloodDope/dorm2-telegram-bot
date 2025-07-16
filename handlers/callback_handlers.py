from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

from config.content import (
    WELCOME_MESSAGE, OFFICIAL_CHANNEL_TEXT, STUDENT_COUNCIL_TEXT,
    FLOOR_CHATS_TEXT, GENERAL_CHAT_TEXT, GUIDE_WEBSITE_TEXT,
    VIDEO_GUIDE_TEXT, CONTACTS_TEXT, ADMIN_CONTACTS, EMERGENCY_CONTACTS,
    TECHNICAL_CONTACTS, COUNCIL_CONTACTS, VIDEO_CATEGORIES,
    FEEDBACK_START, FEEDBACK_RECEIVED
)
from config.settings import get_settings
from keyboards.inline_keyboards import (
    get_main_menu_keyboard, get_back_to_main_keyboard, get_back_keyboard,
    get_student_council_keyboard, get_floor_chats_keyboard,
    get_video_categories_keyboard, get_contacts_keyboard,
    get_feedback_type_keyboard
)
from database.database import (
    update_user_activity, log_section_access, db
)

router = Router()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """Возврат в главное меню"""
    try:
        await update_user_activity(callback.from_user.id)
        
        # Форматируем приветственное сообщение с именем пользователя
        user_first_name = callback.from_user.first_name or "друг"
        welcome_text = WELCOME_MESSAGE.format(first_name=user_first_name)
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в main_menu_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "official_channel")
async def official_channel_callback(callback: CallbackQuery):
    """Официальный канал общежития"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "official_channel")
        
        settings = get_settings()
        # Получаем ссылку из базы данных или настроек
        channel_link = await db.get_setting("official_channel_link") or settings.official_channel_link
        
        text = OFFICIAL_CHANNEL_TEXT.format(
            channel_link=channel_link or "Ссылка будет добавлена позднее"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в official_channel_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "student_council")
async def student_council_callback(callback: CallbackQuery):
    """Студенческий совет"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "student_council")
        
        await callback.message.edit_text(
            STUDENT_COUNCIL_TEXT,
            reply_markup=get_student_council_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в student_council_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "floor_chats")
async def floor_chats_callback(callback: CallbackQuery):
    """Чаты этажей"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "floor_chats")
        
        await callback.message.edit_text(
            FLOOR_CHATS_TEXT,
            reply_markup=get_floor_chats_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в floor_chats_callback: {e}")
        await callback.answer("Произошла ошибка")



@router.callback_query(F.data == "general_chat")
async def general_chat_callback(callback: CallbackQuery):
    """Общий чат общежития"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "general_chat")
        
        text = GENERAL_CHAT_TEXT
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в general_chat_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "guide_website")
async def guide_website_callback(callback: CallbackQuery):
    """Сайт с гайдом"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "guide_website")
        
        settings = get_settings()
        # Получаем ссылку из базы данных или настроек
        guide_website_link = await db.get_setting("guide_website_link") or settings.guide_website_link
        
        text = GUIDE_WEBSITE_TEXT.format(
            guide_website_link=guide_website_link or "Ссылка будет добавлена позднее"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в guide_website_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "video_guide")
async def video_guide_callback(callback: CallbackQuery):
    """Видео-гайды"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "video_guide")
        
        await callback.message.edit_text(
            VIDEO_GUIDE_TEXT,
            reply_markup=get_video_categories_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в video_guide_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data.startswith("video_category_"))
async def video_category_callback(callback: CallbackQuery):
    """Конкретная категория видео"""
    try:
        await update_user_activity(callback.from_user.id)
        
        category_id = callback.data.split("video_category_")[1]
        category_info = VIDEO_CATEGORIES.get(category_id)
        
        if not category_info:
            await callback.answer("Категория не найдена")
            return
        
        # Получаем видео из базы данных
        videos = await db.get_videos_by_category(category_id)
        
        if videos:
            text = f"""
🎬 <b>{category_info['name']}</b>

{category_info['description']}

Найдено видео: {len(videos)}
"""
            
            await callback.message.edit_text(text, reply_markup=get_back_keyboard("video_guide"))
            
            # Отправляем видео
            for video in videos[:5]:  # Ограничиваем до 5 видео за раз
                try:
                    await callback.message.answer_video(
                        video=video["file_id"],
                        caption=f"📹 <b>{video['title']}</b>\n\n{video['description']}"
                    )
                except Exception as video_error:
                    logger.error(f"Ошибка при отправке видео {video['id']}: {video_error}")
        else:
            text = f"""
🎬 <b>{category_info['name']}</b>

{category_info['description']}

К сожалению, видео в этой категории пока не добавлены.
Они появятся в ближайшее время!
"""
            await callback.message.edit_text(
                text,
                reply_markup=get_back_keyboard("video_guide")
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в video_category_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "contacts")
async def contacts_callback(callback: CallbackQuery):
    """Важные контакты"""
    try:
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "contacts")
        
        await callback.message.edit_text(
            CONTACTS_TEXT,
            reply_markup=get_back_to_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в contacts_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "contacts_admin")
async def contacts_admin_callback(callback: CallbackQuery):
    """Контакты администрации"""
    try:
        await update_user_activity(callback.from_user.id)
        
        await callback.message.edit_text(
            ADMIN_CONTACTS,
            reply_markup=get_back_keyboard("contacts")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в contacts_admin_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "contacts_emergency")
async def contacts_emergency_callback(callback: CallbackQuery):
    """Экстренные контакты"""
    try:
        await update_user_activity(callback.from_user.id)
        
        await callback.message.edit_text(
            EMERGENCY_CONTACTS,
            reply_markup=get_back_keyboard("contacts")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в contacts_emergency_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "contacts_technical")
async def contacts_technical_callback(callback: CallbackQuery):
    """Технические контакты"""
    try:
        await update_user_activity(callback.from_user.id)
        
        await callback.message.edit_text(
            TECHNICAL_CONTACTS,
            reply_markup=get_back_keyboard("contacts")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в contacts_technical_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "contacts_council")
async def contacts_council_callback(callback: CallbackQuery):
    """Контакты студенческого совета"""
    try:
        await update_user_activity(callback.from_user.id)
        
        await callback.message.edit_text(
            COUNCIL_CONTACTS,
            reply_markup=get_back_keyboard("contacts")
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в contacts_council_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "feedback")
async def feedback_callback(callback: CallbackQuery, state: FSMContext):
    """Обратная связь"""
    try:
        # Ленивый импорт для избежания циклических зависимостей
        from handlers.feedback_handlers import FeedbackStates
        
        await update_user_activity(callback.from_user.id)
        await log_section_access(callback.from_user.id, "feedback")
        
        # Очищаем предыдущее состояние и устанавливаем новое
        await state.clear()
        await state.update_data(feedback_type="general")
        await state.set_state(FeedbackStates.waiting_for_message)
        
        feedback_text = """
<b>📝 Обратная связь</b>

Мы ценим ваше мнение! Помогите нам стать лучше! Ваше сообщение будет передано администратору бота.

Напишите ваше сообщение:
"""
        
        await callback.message.edit_text(
            feedback_text,
            reply_markup=get_back_to_main_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в feedback_callback: {e}")
        await callback.answer("Произошла ошибка")



def register_callback_handlers(dp):
    """Регистрация обработчиков callback'ов"""
    dp.include_router(router) 