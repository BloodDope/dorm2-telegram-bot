import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config.settings import get_settings
from database.database import init_db
from handlers import register_handlers
from loguru import logger

async def main():
    """Основная функция запуска бота"""
    bot = None
    try:
        # Загружаем настройки
        settings = get_settings()
        
        # Инициализация базы данных
        await init_db()
        logger.info("База данных инициализирована")
        
        # Инициализация бота и диспетчера
        bot = Bot(
            token=settings.bot_token,
            parse_mode=ParseMode.HTML
        )
        dp = Dispatcher()
        
        # Регистрация обработчиков
        register_handlers(dp)
        logger.info("Обработчики зарегистрированы")
        
        # Запуск бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        if bot:
            await bot.session.close()

if __name__ == "__main__":
    # Настройка логирования
    logger.add("logs/bot.log", rotation="1 day", retention="7 days")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем") 