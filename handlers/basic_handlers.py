from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from loguru import logger

from config.content import WELCOME_MESSAGE, HELP_MESSAGE
from keyboards.inline_keyboards import get_main_menu_keyboard
from database.database import add_user, update_user_activity

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        user = message.from_user
        if not user:
            return
        
        # Добавляем пользователя в базу данных
        await add_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )
        
        # Обновляем активность
        await update_user_activity(user.id)
        
        # Всегда показываем приветственное сообщение с меню
        user_first_name = user.first_name or "друг"
        welcome_text = WELCOME_MESSAGE.format(first_name=user_first_name)
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
        
        logger.info(f"Пользователь {user.id} ({user.username or 'без username'}) запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer(
            "Произошла ошибка при запуске бота. Попробуйте еще раз.",
            reply_markup=get_main_menu_keyboard()
        )

@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    try:
        user = message.from_user
        if not user:
            return
        
        # Обновляем активность
        await update_user_activity(user.id)
        
        # Отправляем справочное сообщение
        await message.answer(
            HELP_MESSAGE,
            reply_markup=get_main_menu_keyboard()
        )
        
        logger.info(f"Пользователь {user.id} запросил помощь")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /help: {e}")
        await message.answer(
            "Произошла ошибка при получении справки.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(F.text)
async def handle_text_messages(message: Message):
    """Обработчик текстовых сообщений"""
    try:
        user = message.from_user
        if not user:
            return
        
        # Обновляем активность
        await update_user_activity(user.id)
        
        # Если сообщение не является командой, предлагаем воспользоваться меню
        await message.answer(
            "🤖 Для навигации используйте кнопки меню ниже.\n\n"
            "Если у вас есть вопрос или предложение, воспользуйтесь разделом "
            "\"📝 Обратная связь\" в главном меню.",
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")

def register_basic_handlers(dp):
    """Регистрация основных обработчиков"""
    dp.include_router(router) 