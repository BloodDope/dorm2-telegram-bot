#!/usr/bin/env python3
"""
Быстрый возврат к SQLite для Railway.app
Запустите этот скрипт если PostgreSQL не работает
"""

import os
import shutil

def revert_to_sqlite():
    """Возврат к SQLite конфигурации"""
    
    print("🔄 Возврат к SQLite...")
    
    # 1. Восстановить requirements.txt
    requirements_content = """aiofiles==23.2.1
aiogram==3.3.0
aiohttp==3.9.5
aiosignal==1.4.0
aiosqlite==0.20.0
annotated-types==0.7.0
async-timeout==4.0.3
attrs==25.3.0
certifi==2025.7.14
frozenlist==1.7.0
idna==3.10
loguru==0.7.2
magic-filter==1.0.12
multidict==6.6.3
propcache==0.3.2
pydantic==2.5.3
pydantic_core==2.14.6
python-dotenv==1.0.0
typing_extensions==4.14.1
yarl==1.20.1
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    # 2. Восстановить settings.py
    settings_content = '''import os
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
    database_path: str = "/tmp/bot.db"  # Для Railway.app используем /tmp
    
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
        database_path=os.getenv("DATABASE_PATH", "/tmp/bot.db"),
        official_channel_link=os.getenv("OFFICIAL_CHANNEL_LINK", ""),
        general_chat_link=os.getenv("GENERAL_CHAT_LINK", ""),
        guide_website_link=os.getenv("GUIDE_WEBSITE_LINK", ""),
        stats_enabled=os.getenv("STATS_ENABLED", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )
'''
    
    with open("config/settings.py", "w") as f:
        f.write(settings_content)
    
    print("✅ SQLite конфигурация восстановлена")
    print("🚀 Теперь запустите: git add -A && git commit -m 'Revert to SQLite' && git push")
    print("📝 Railway.app автоматически перезапустит бот")

if __name__ == "__main__":
    revert_to_sqlite() 