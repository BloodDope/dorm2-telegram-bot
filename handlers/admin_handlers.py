from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

from config.content import ADMIN_PANEL_TEXT, STATS_TEXT
from config.settings import get_settings
from keyboards.inline_keyboards import (
    get_admin_panel_keyboard, get_admin_content_keyboard, 
    get_admin_stats_keyboard, get_broadcast_confirm_keyboard,
    get_video_management_keyboard, get_main_menu_keyboard
)
from database.database import is_admin, db

router = Router()

# States для административных действий
class AdminStates(StatesGroup):
    waiting_for_broadcast_message = State()
    waiting_for_setting_value = State()
    waiting_for_video_upload = State()

async def check_admin_rights(user_id: int) -> bool:
    """Проверка прав администратора"""
    settings = get_settings()
    return user_id in settings.admin_ids or await is_admin(user_id)

@router.message(Command("admin"))
async def admin_command(message: Message):
    """Команда входа в административную панель"""
    try:
        if not await check_admin_rights(message.from_user.id):
            await message.answer("❌ У вас нет прав администратора.")
            return
        
        await message.answer(
            ADMIN_PANEL_TEXT,
            reply_markup=get_admin_panel_keyboard()
        )
        
        logger.info(f"Администратор {message.from_user.id} вошел в панель")
        
    except Exception as e:
        logger.error(f"Ошибка в admin_command: {e}")
        await message.answer("Произошла ошибка при входе в административную панель.")

@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Возврат в административную панель"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        await callback.message.edit_text(
            ADMIN_PANEL_TEXT,
            reply_markup=get_admin_panel_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_panel_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    """Статистика бота"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        # Получаем статистику из базы данных
        user_stats = await db.get_user_stats()
        feedback_stats = await db.get_feedback_stats()
        popular_sections = await db.get_popular_sections()
        
        # Форматируем популярные разделы
        popular_text = ""
        if popular_sections:
            for i, (section, count) in enumerate(popular_sections, 1):
                section_names = {
                    "official_channel": "📢 Официальный канал",
                    "student_council": "💡 Студенческий совет", 
                    "floor_chats": "🗣 Чаты этажей",
                    "general_chat": "👥 Общий чат",
                    "guide_website": "📚 Сайт с гайдом",
                    "video_guide": "🎬 Видео-гайды",
                    "contacts": "📞 Контакты",
                    "feedback": "📝 Обратная связь"
                }
                section_name = section_names.get(section, section)
                popular_text += f"{i}. {section_name}: {count}\n"
        else:
            popular_text = "Данных пока нет"
        
        stats_text = STATS_TEXT.format(
            total_users=user_stats.get("total_users", 0),
            active_today=user_stats.get("active_today", 0),
            active_week=user_stats.get("active_week", 0),
            active_month=user_stats.get("active_month", 0),
            popular_sections=popular_text,
            new_feedback=feedback_stats.get("new_feedback", 0),
            total_feedback=feedback_stats.get("total_feedback", 0)
        )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=get_admin_stats_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_stats_callback: {e}")
        await callback.answer("Произошла ошибка при получении статистики")

@router.callback_query(F.data == "refresh_stats")
async def refresh_stats_callback(callback: CallbackQuery):
    """Обновление статистики"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        await callback.answer("📊 Статистика обновлена!")
        # Повторно вызываем отображение статистики
        await admin_stats_callback(callback)
        
    except Exception as e:
        logger.error(f"Ошибка в refresh_stats_callback: {e}")
        await callback.answer("Произошла ошибка при обновлении статистики")

@router.callback_query(F.data == "admin_edit_content")
async def admin_edit_content_callback(callback: CallbackQuery):
    """Редактирование контента"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        text = """
📝 <b>Редактирование контента</b>

Выберите, что хотите изменить:

• Ссылки на каналы и чаты
• Контактную информацию
• Ссылки на чаты этажей
• Другие настройки

Все изменения сохраняются автоматически.
"""
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_content_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_edit_content_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    """Массовая рассылка"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        await state.set_state(AdminStates.waiting_for_broadcast_message)
        
        text = """
📨 <b>Массовая рассылка</b>

Напишите сообщение, которое будет отправлено всем пользователям бота.

⚠️ <b>Внимание:</b>
• Сообщение будет отправлено ВСЕМ пользователям
• Поддерживается HTML-разметка
• Можно прикреплять изображения и видео
• Для отмены используйте /cancel

Пример форматирования:
<b>Жирный текст</b>
<i>Курсив</i>
<code>Код</code>
"""
        
        await callback.message.edit_text(text)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_broadcast_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обработка сообщения для рассылки"""
    try:
        if not await check_admin_rights(message.from_user.id):
            await message.answer("❌ У вас нет прав администратора.")
            await state.clear()
            return
        
        # Сохраняем сообщение в состоянии
        broadcast_data = {
            "text": message.text,
            "message_id": message.message_id
        }
        
        # Если есть фото/видео, сохраняем их
        if message.photo:
            broadcast_data["photo"] = message.photo[-1].file_id
            broadcast_data["caption"] = message.caption
        elif message.video:
            broadcast_data["video"] = message.video.file_id
            broadcast_data["caption"] = message.caption
        
        await state.update_data(broadcast_data=broadcast_data)
        
        # Получаем количество пользователей
        user_stats = await db.get_user_stats()
        total_users = user_stats.get("total_users", 0)
        
        preview_text = f"""
📨 <b>Предварительный просмотр рассылки</b>

<b>Получателей:</b> {total_users} пользователей

<b>Содержимое:</b>
{message.text or message.caption or "Медиа-файл"}

⚠️ Убедитесь, что сообщение корректно отформатировано!
"""
        
        await message.answer(
            preview_text,
            reply_markup=get_broadcast_confirm_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка в process_broadcast_message: {e}")
        await message.answer("Произошла ошибка при подготовке рассылки.")
        await state.clear()

@router.callback_query(F.data == "broadcast_confirm")
async def broadcast_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение массовой рассылки"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        data = await state.get_data()
        broadcast_data = data.get("broadcast_data")
        
        if not broadcast_data:
            await callback.answer("Данные рассылки не найдены")
            return
        
        await callback.message.edit_text("📨 Рассылка начата...")
        
        # Получаем всех пользователей
        async with db.db_path and db.db_path as conn:
            cursor = await conn.execute("SELECT user_id FROM users WHERE is_active = TRUE")
            users = await cursor.fetchall()
        
        sent_count = 0
        failed_count = 0
        
        for (user_id,) in users:
            try:
                if "photo" in broadcast_data:
                    await callback.bot.send_photo(
                        chat_id=user_id,
                        photo=broadcast_data["photo"],
                        caption=broadcast_data.get("caption", "")
                    )
                elif "video" in broadcast_data:
                    await callback.bot.send_video(
                        chat_id=user_id,
                        video=broadcast_data["video"],
                        caption=broadcast_data.get("caption", "")
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=user_id,
                        text=broadcast_data["text"]
                    )
                sent_count += 1
            except Exception as send_error:
                failed_count += 1
                logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {send_error}")
        
        # Сохраняем статистику рассылки
        async with db.db_path and db.db_path as conn:
            await conn.execute("""
                INSERT INTO broadcasts (admin_id, message, sent_count, failed_count, completed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                callback.from_user.id,
                broadcast_data.get("text", "Медиа-сообщение"),
                sent_count,
                failed_count,
                datetime.now()
            ))
            await conn.commit()
        
        result_text = f"""
✅ <b>Рассылка завершена!</b>

📊 <b>Статистика:</b>
• Отправлено: {sent_count}
• Ошибок: {failed_count}
• Общий охват: {sent_count}/{sent_count + failed_count}

Время завершения: {datetime.now().strftime("%H:%M:%S")}
"""
        
        await callback.message.edit_text(
            result_text,
            reply_markup=get_admin_panel_keyboard()
        )
        
        await state.clear()
        await callback.answer()
        
        logger.info(f"Рассылка завершена: {sent_count} отправлено, {failed_count} ошибок")
        
    except Exception as e:
        logger.error(f"Ошибка в broadcast_confirm_callback: {e}")
        await callback.answer("Произошла ошибка при рассылке")
        await state.clear()

@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    try:
        await state.clear()
        await callback.message.edit_text(
            "❌ Рассылка отменена.",
            reply_markup=get_admin_panel_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в broadcast_cancel_callback: {e}")
        await callback.answer("Произошла ошибка")

@router.callback_query(F.data == "admin_feedback")
async def admin_feedback_callback(callback: CallbackQuery):
    """Просмотр обратной связи"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        # Получаем непрочитанную обратную связь
        feedback_list = await db.get_unread_feedback()
        
        if not feedback_list:
            text = """
💬 <b>Обратная связь</b>

📭 Новых сообщений нет.

Все сообщения обратной связи обработаны.
"""
        else:
            text = f"""
💬 <b>Обратная связь</b>

📬 Новых сообщений: {len(feedback_list)}

<b>Последние сообщения:</b>
"""
            
            for feedback in feedback_list[:5]:  # Показываем только первые 5
                username = feedback["username"] or "Неизвестно"
                feedback_type = feedback["feedback_type"]
                created_at = feedback["created_at"]
                message_preview = feedback["message"][:100] + "..." if len(feedback["message"]) > 100 else feedback["message"]
                
                text += f"""

📝 <b>От:</b> @{username} (ID: {feedback["user_id"]})
📅 <b>Дата:</b> {created_at}
🏷 <b>Тип:</b> {feedback_type}
💭 <b>Сообщение:</b> {message_preview}
"""
        
        await callback.message.edit_text(
            text,
            reply_markup=get_admin_panel_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_feedback_callback: {e}")
        await callback.answer("Произошла ошибка при получении обратной связи")

@router.callback_query(F.data == "admin_videos")
async def admin_videos_callback(callback: CallbackQuery):
    """Управление видео"""
    try:
        if not await check_admin_rights(callback.from_user.id):
            await callback.answer("❌ У вас нет прав администратора.")
            return
        
        text = """
🎬 <b>Управление видео-гайдами</b>

Выберите категорию для просмотра или добавления видео:

Каждая категория может содержать до 10 видео.
Поддерживаемые форматы: MP4, AVI, MOV
Максимальный размер: 50 МБ
"""
        
        await callback.message.edit_text(
            text,
            reply_markup=get_video_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_videos_callback: {e}")
        await callback.answer("Произошла ошибка")

# Обработчик для отмены админских действий
@router.message(Command("cancel"))
async def cancel_admin_action(message: Message, state: FSMContext):
    """Отмена текущего административного действия"""
    try:
        current_state = await state.get_state()
        if current_state:
            await state.clear()
            await message.answer(
                "❌ Действие отменено.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await message.answer(
                "Нет активных действий для отмены.",
                reply_markup=get_main_menu_keyboard()
            )
    except Exception as e:
        logger.error(f"Ошибка в cancel_admin_action: {e}")

def register_admin_handlers(dp):
    """Регистрация административных обработчиков"""
    dp.include_router(router) 