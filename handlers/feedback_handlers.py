from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

from config.content import FEEDBACK_RECEIVED
from config.settings import get_settings
from keyboards.inline_keyboards import get_main_menu_keyboard
from database.database import update_user_activity, db

router = Router()

class FeedbackStates(StatesGroup):
    waiting_for_message = State()

async def notify_admin_about_feedback(message: Message, user, feedback_type: str):
    """Уведомляем администратора о новом сообщении обратной связи"""
    try:
        settings = get_settings()
        bot = message.bot
        
        # Формируем сообщение для администратора
        admin_notification = f"""
🔔 <b>Новое сообщение обратной связи</b>

👤 <b>От пользователя:</b> {user.first_name or ''} {user.last_name or ''} (@{user.username or 'без username'})
🆔 <b>ID:</b> {user.id}
📝 <b>Тип:</b> {feedback_type}
📅 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

💬 <b>Сообщение:</b>
{message.text}
"""
        
        # Отправляем уведомление всем администраторам
        for admin_id in settings.admin_ids:
            try:
                await bot.send_message(admin_id, admin_notification)
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление администратору {admin_id}: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления администратору: {e}")

@router.message(FeedbackStates.waiting_for_message)
async def process_feedback_message(message: Message, state: FSMContext):
    """Обработка сообщения обратной связи"""
    try:
        user = message.from_user
        await update_user_activity(user.id)
        
        # Получаем данные из состояния
        data = await state.get_data()
        feedback_type = data.get("feedback_type", "general")
        
        # Сохраняем обратную связь в базу данных
        feedback_id = await db.add_feedback(
            user_id=user.id,
            feedback_type=feedback_type,
            message=message.text
        )
        
        if feedback_id:
            # Отправляем подтверждение пользователю
            confirmation_text = FEEDBACK_RECEIVED
            
            await message.answer(
                confirmation_text,
                reply_markup=get_main_menu_keyboard()
            )
            
            # Уведомляем администратора о новом сообщении
            await notify_admin_about_feedback(message, user, feedback_type)
            
            logger.info(f"Получена обратная связь от пользователя {user.id}: {feedback_type}")
        else:
            await message.answer(
                "❌ Произошла ошибка при сохранении вашего сообщения. Попробуйте еще раз.",
                reply_markup=get_main_menu_keyboard()
            )
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка в process_feedback_message: {e}")
        await message.answer(
            "Произошла ошибка при обработке вашего сообщения.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()

def register_feedback_handlers(dp):
    """Регистрация обработчиков обратной связи"""
    dp.include_router(router) 