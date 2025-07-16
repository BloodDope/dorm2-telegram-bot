import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config.settings import get_settings
from database.database import init_db
from handlers import register_handlers
from loguru import logger
from keep_alive import create_web_server, start_web_server

async def main():
    """Основная функция запуска бота"""
    bot = None
    web_runner = None
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
        
        # Запуск HTTP-сервера для предотвращения автосна (если на Render.com)
        if os.getenv("RENDER"):
            web_app = await create_web_server()
            port = int(os.getenv("PORT", 8000))
            web_runner = await start_web_server(web_app, port)
            logger.info(f"HTTP сервер запущен на порту {port} для предотвращения автосна")
        
        # Запуск бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        if bot:
            await bot.session.close()
        if web_runner:
            await web_runner.cleanup()

if __name__ == "__main__":
    # Настройка логирования
    logger.add("logs/bot.log", rotation="1 day", retention="7 days")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем") 