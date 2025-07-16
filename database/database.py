import aiosqlite
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
from config.settings import get_settings
import os

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    async def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Таблица статистики использования разделов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS section_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    section_name TEXT,
                    access_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица обратной связи
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    feedback_type TEXT,
                    message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE,
                    admin_response TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица настроек и ссылок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица видео
            await db.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    file_id TEXT,
                    file_path TEXT,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Таблица ссылок на чаты этажей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS floor_chats (
                    floor_number INTEGER PRIMARY KEY,
                    chat_link TEXT,
                    chat_title TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица массовых рассылок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    message TEXT,
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (admin_id) REFERENCES users (user_id)
                )
            """)
            
            await db.commit()
            logger.info("База данных SQLite инициализирована")

    # Методы для работы с пользователями
    
    async def user_exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT 1 FROM users WHERE user_id = ?
                """, (user_id,))
                result = await cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя {user_id}: {e}")
            return False
    
    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, first_name, last_name, datetime.now()))
                await db.commit()
                logger.info(f"Пользователь {user_id} добавлен/обновлен")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            return False
    
    async def update_user_activity(self, user_id: int):
        """Обновление времени последней активности пользователя"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users SET last_activity = ? WHERE user_id = ?
                """, (datetime.now(), user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении активности пользователя {user_id}: {e}")
    
    async def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT is_admin FROM users WHERE user_id = ?
                """, (user_id,))
                result = await cursor.fetchone()
                return result[0] if result else False
        except Exception as e:
            logger.error(f"Ошибка при проверке прав администратора {user_id}: {e}")
            return False
    
    async def set_admin(self, user_id: int, is_admin: bool = True):
        """Установка прав администратора"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE users SET is_admin = ? WHERE user_id = ?
                """, (is_admin, user_id))
                await db.commit()
                logger.info(f"Права администратора для {user_id} изменены на {is_admin}")
        except Exception as e:
            logger.error(f"Ошибка при изменении прав администратора {user_id}: {e}")
    
    # Методы для работы со статистикой
    
    async def log_section_access(self, user_id: int, section_name: str):
        """Логирование обращения к разделу"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO section_stats (user_id, section_name)
                    VALUES (?, ?)
                """, (user_id, section_name))
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка при логировании доступа к разделу: {e}")
    
    async def get_user_stats(self) -> Dict:
        """Получение статистики пользователей"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Общее количество пользователей
                cursor = await db.execute("SELECT COUNT(*) FROM users")
                total_users = (await cursor.fetchone())[0]
                
                # Активные пользователи за сегодня
                today = datetime.now().date()
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(last_activity) = ?
                """, (today,))
                active_today = (await cursor.fetchone())[0]
                
                # Активные пользователи за неделю
                week_ago = datetime.now() - timedelta(days=7)
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity >= ?
                """, (week_ago,))
                active_week = (await cursor.fetchone())[0]
                
                # Активные пользователи за месяц
                month_ago = datetime.now() - timedelta(days=30)
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity >= ?
                """, (month_ago,))
                active_month = (await cursor.fetchone())[0]
                
                return {
                    "total_users": total_users,
                    "active_today": active_today,
                    "active_week": active_week,
                    "active_month": active_month
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователей: {e}")
            return {}
    
    async def get_popular_sections(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Получение популярных разделов"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT section_name, COUNT(*) as access_count
                    FROM section_stats
                    WHERE access_time >= ?
                    GROUP BY section_name
                    ORDER BY access_count DESC
                    LIMIT ?
                """, (datetime.now() - timedelta(days=30), limit))
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Ошибка при получении популярных разделов: {e}")
            return []
    
    # Методы для работы с обратной связью
    
    async def add_feedback(self, user_id: int, feedback_type: str, message: str) -> int:
        """Добавление обратной связи"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO feedback (user_id, feedback_type, message)
                    VALUES (?, ?, ?)
                """, (user_id, feedback_type, message))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при добавлении обратной связи: {e}")
            return 0
    
    async def get_feedback_stats(self) -> Dict:
        """Получение статистики обратной связи"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Новые сообщения (непрочитанные)
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM feedback WHERE is_read = FALSE
                """)
                new_feedback = (await cursor.fetchone())[0]
                
                # Всего сообщений
                cursor = await db.execute("SELECT COUNT(*) FROM feedback")
                total_feedback = (await cursor.fetchone())[0]
                
                return {
                    "new_feedback": new_feedback,
                    "total_feedback": total_feedback
                }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики обратной связи: {e}")
            return {}
    
    async def get_unread_feedback(self) -> List[Dict]:
        """Получение непрочитанной обратной связи"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT f.id, f.user_id, f.feedback_type, f.message, 
                           f.created_at, u.username, u.first_name, u.last_name
                    FROM feedback f
                    LEFT JOIN users u ON f.user_id = u.user_id
                    WHERE f.is_read = FALSE
                    ORDER BY f.created_at DESC
                """)
                rows = await cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "feedback_type": row[2],
                        "message": row[3],
                        "created_at": row[4],
                        "username": row[5],
                        "first_name": row[6],
                        "last_name": row[7]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Ошибка при получении непрочитанной обратной связи: {e}")
            return []
    
    # Методы для работы с настройками
    
    async def get_setting(self, key: str) -> Optional[str]:
        """Получение настройки по ключу"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT value FROM bot_settings WHERE key = ?
                """, (key,))
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Ошибка при получении настройки {key}: {e}")
            return None
    
    async def set_setting(self, key: str, value: str):
        """Установка настройки"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now()))
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка при установке настройки {key}: {e}")
    
    # Методы для работы с видео
    
    async def add_video(self, category: str, title: str, description: str, 
                       file_id: str, file_path: str = None) -> int:
        """Добавление видео"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO videos (category, title, description, file_id, file_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (category, title, description, file_id, file_path))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Ошибка при добавлении видео: {e}")
            return 0
    
    async def get_videos_by_category(self, category: str) -> List[Dict]:
        """Получение видео по категории"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT id, title, description, file_id, file_path
                    FROM videos
                    WHERE category = ? AND is_active = TRUE
                    ORDER BY added_at DESC
                """, (category,))
                rows = await cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "title": row[1],
                        "description": row[2],
                        "file_id": row[3],
                        "file_path": row[4]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Ошибка при получении видео категории {category}: {e}")
            return []
    
    # Методы для работы с чатами этажей
    
    async def set_floor_chat(self, floor_number: int, chat_link: str, chat_title: str = None):
        """Установка ссылки на чат этажа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO floor_chats 
                    (floor_number, chat_link, chat_title, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (floor_number, chat_link, chat_title, datetime.now()))
                await db.commit()
        except Exception as e:
            logger.error(f"Ошибка при установке чата этажа {floor_number}: {e}")
    
    async def get_floor_chat(self, floor_number: int) -> Optional[Dict]:
        """Получение ссылки на чат этажа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT chat_link, chat_title FROM floor_chats 
                    WHERE floor_number = ?
                """, (floor_number,))
                result = await cursor.fetchone()
                
                if result:
                    return {
                        "chat_link": result[0],
                        "chat_title": result[1]
                    }
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении чата этажа {floor_number}: {e}")
            return None

# Глобальный экземпляр базы данных
db = Database(get_settings().database_path)

async def init_db():
    """Инициализация базы данных"""
    await db.init_database()

# Функции-обертки для удобства
async def add_user(user_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None) -> bool:
    return await db.add_user(user_id, username, first_name, last_name)

async def update_user_activity(user_id: int):
    await db.update_user_activity(user_id)

async def is_admin(user_id: int) -> bool:
    return await db.is_admin(user_id)

async def log_section_access(user_id: int, section_name: str):
    await db.log_section_access(user_id, section_name)

async def user_exists(user_id: int) -> bool:
    return await db.user_exists(user_id) 