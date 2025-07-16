import os
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

@dataclass
class Settings:
    """Настройки приложения"""
    # Основные настройки бота
    bot_token: str
    admin_ids: List[int]
    
    # Настройки базы данных
    database_path: str = "data/bot.db"
    
    # Контент настройки
    official_channel_link: str = ""
    general_chat_link: str = ""
    guide_website_link: str = ""
    
    # Настройки статистики
    stats_enabled: bool = True
    
    # Настройки логирования
    log_level: str = "INFO"

def get_settings() -> Settings:
    """Получение настроек из переменных окружения"""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")
    
    # Получаем ID администраторов
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = []
    if admin_ids_str:
        try:
            admin_ids = [int(id_str.strip()) for id_str in admin_ids_str.split(",")]
        except ValueError:
            raise ValueError("Некорректный формат ADMIN_IDS")
    
    return Settings(
        bot_token=bot_token,
        admin_ids=admin_ids,
        database_path=os.getenv("DATABASE_PATH", "data/bot.db"),
        official_channel_link=os.getenv("OFFICIAL_CHANNEL_LINK", ""),
        general_chat_link=os.getenv("GENERAL_CHAT_LINK", ""),
        guide_website_link=os.getenv("GUIDE_WEBSITE_LINK", ""),
        stats_enabled=os.getenv("STATS_ENABLED", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO")
    ) 