import asyncpg
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
from config.settings import get_settings

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def create_pool(self):
        """Создание пула соединений"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Пул соединений PostgreSQL создан")
        except Exception as e:
            logger.error(f"Ошибка создания пула соединений: {e}")
            raise
    
    async def close_pool(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Пул соединений PostgreSQL закрыт")
    
    async def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        if not self.pool:
            await self.create_pool()
            
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Таблица статистики использования разделов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS section_stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    section_name TEXT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица обратной связи
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    feedback_type TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE,
                    admin_response TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Таблица настроек и ссылок
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица видео
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id SERIAL PRIMARY KEY,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    file_id TEXT,
                    file_path TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Таблица ссылок на чаты этажей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS floor_chats (
                    floor_number INTEGER PRIMARY KEY,
                    chat_link TEXT,
                    chat_title TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица массовых рассылок
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id SERIAL PRIMARY KEY,
                    admin_id BIGINT,
                    message TEXT,
                    sent_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES users (user_id)
                )
            """)
            
            logger.info("База данных PostgreSQL инициализирована")

    # Методы для работы с пользователями
    
    async def user_exists(self, user_id: int) -> bool:
        """Проверка существования пользователя"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT 1 FROM users WHERE user_id = $1
                """, user_id)
                return result is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя {user_id}: {e}")
            return False
    
    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, last_activity)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        last_activity = EXCLUDED.last_activity
                """, user_id, username, first_name, last_name, datetime.now())
                logger.info(f"Пользователь {user_id} добавлен/обновлен")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            return False
    
    async def update_user_activity(self, user_id: int):
        """Обновление времени последней активности пользователя"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users SET last_activity = $1 WHERE user_id = $2
                """, datetime.now(), user_id)
        except Exception as e:
            logger.error(f"Ошибка при обновлении активности пользователя {user_id}: {e}")
    
    async def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT is_admin FROM users WHERE user_id = $1
                """, user_id)
                return result if result else False
        except Exception as e:
            logger.error(f"Ошибка при проверке прав администратора {user_id}: {e}")
            return False
    
    async def set_admin(self, user_id: int, is_admin: bool = True):
        """Установка прав администратора"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users SET is_admin = $1 WHERE user_id = $2
                """, is_admin, user_id)
                logger.info(f"Права администратора для {user_id} изменены на {is_admin}")
        except Exception as e:
            logger.error(f"Ошибка при изменении прав администратора {user_id}: {e}")
    
    # Методы для работы со статистикой
    
    async def log_section_access(self, user_id: int, section_name: str):
        """Логирование обращения к разделу"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO section_stats (user_id, section_name)
                    VALUES ($1, $2)
                """, user_id, section_name)
        except Exception as e:
            logger.error(f"Ошибка при логировании доступа к разделу: {e}")
    
    async def get_user_stats(self) -> Dict:
        """Получение статистики пользователей"""
        try:
            async with self.pool.acquire() as conn:
                # Общее количество пользователей
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                # Активные пользователи за сегодня
                today = datetime.now().date()
                active_today = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE DATE(last_activity) = $1
                """, today)
                
                # Активные пользователи за неделю
                week_ago = datetime.now() - timedelta(days=7)
                active_week = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity >= $1
                """, week_ago)
                
                # Активные пользователи за месяц
                month_ago = datetime.now() - timedelta(days=30)
                active_month = await conn.fetchval("""
                    SELECT COUNT(*) FROM users 
                    WHERE last_activity >= $1
                """, month_ago)
                
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
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT section_name, COUNT(*) as access_count
                    FROM section_stats
                    WHERE access_time >= $1
                    GROUP BY section_name
                    ORDER BY access_count DESC
                    LIMIT $2
                """, datetime.now() - timedelta(days=30), limit)
                return [(row['section_name'], row['access_count']) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении популярных разделов: {e}")
            return []
    
    # Методы для работы с обратной связью
    
    async def add_feedback(self, user_id: int, feedback_type: str, message: str) -> int:
        """Добавление обратной связи"""
        try:
            async with self.pool.acquire() as conn:
                feedback_id = await conn.fetchval("""
                    INSERT INTO feedback (user_id, feedback_type, message)
                    VALUES ($1, $2, $3)
                    RETURNING id
                """, user_id, feedback_type, message)
                return feedback_id
        except Exception as e:
            logger.error(f"Ошибка при добавлении обратной связи: {e}")
            return 0
    
    async def get_feedback_stats(self) -> Dict:
        """Получение статистики обратной связи"""
        try:
            async with self.pool.acquire() as conn:
                # Новые сообщения (непрочитанные)
                new_feedback = await conn.fetchval("""
                    SELECT COUNT(*) FROM feedback WHERE is_read = FALSE
                """)
                
                # Всего сообщений
                total_feedback = await conn.fetchval("SELECT COUNT(*) FROM feedback")
                
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
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT f.id, f.user_id, f.feedback_type, f.message, 
                           f.created_at, u.username, u.first_name, u.last_name
                    FROM feedback f
                    LEFT JOIN users u ON f.user_id = u.user_id
                    WHERE f.is_read = FALSE
                    ORDER BY f.created_at DESC
                """)
                
                return [
                    {
                        "id": row['id'],
                        "user_id": row['user_id'],
                        "feedback_type": row['feedback_type'],
                        "message": row['message'],
                        "created_at": row['created_at'],
                        "username": row['username'],
                        "first_name": row['first_name'],
                        "last_name": row['last_name']
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
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("""
                    SELECT value FROM bot_settings WHERE key = $1
                """, key)
                return result
        except Exception as e:
            logger.error(f"Ошибка при получении настройки {key}: {e}")
            return None
    
    async def set_setting(self, key: str, value: str):
        """Установка настройки"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bot_settings (key, value, updated_at)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = EXCLUDED.updated_at
                """, key, value, datetime.now())
        except Exception as e:
            logger.error(f"Ошибка при установке настройки {key}: {e}")
    
    # Методы для работы с видео
    
    async def add_video(self, category: str, title: str, description: str, 
                       file_id: str, file_path: str = None) -> int:
        """Добавление видео"""
        try:
            async with self.pool.acquire() as conn:
                video_id = await conn.fetchval("""
                    INSERT INTO videos (category, title, description, file_id, file_path)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """, category, title, description, file_id, file_path)
                return video_id
        except Exception as e:
            logger.error(f"Ошибка при добавлении видео: {e}")
            return 0
    
    async def get_videos_by_category(self, category: str) -> List[Dict]:
        """Получение видео по категории"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, title, description, file_id, file_path
                    FROM videos
                    WHERE category = $1 AND is_active = TRUE
                    ORDER BY added_at DESC
                """, category)
                
                return [
                    {
                        "id": row['id'],
                        "title": row['title'],
                        "description": row['description'],
                        "file_id": row['file_id'],
                        "file_path": row['file_path']
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
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO floor_chats 
                    (floor_number, chat_link, chat_title, updated_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (floor_number) DO UPDATE SET
                        chat_link = EXCLUDED.chat_link,
                        chat_title = EXCLUDED.chat_title,
                        updated_at = EXCLUDED.updated_at
                """, floor_number, chat_link, chat_title, datetime.now())
        except Exception as e:
            logger.error(f"Ошибка при установке чата этажа {floor_number}: {e}")
    
    async def get_floor_chat(self, floor_number: int) -> Optional[Dict]:
        """Получение ссылки на чат этажа"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT chat_link, chat_title FROM floor_chats 
                    WHERE floor_number = $1
                """, floor_number)
                
                if row:
                    return {
                        "chat_link": row['chat_link'],
                        "chat_title": row['chat_title']
                    }
                return None
        except Exception as e:
            logger.error(f"Ошибка при получении чата этажа {floor_number}: {e}")
            return None

# Глобальный экземпляр базы данных
db = None

async def init_db():
    """Инициализация базы данных"""
    global db
    settings = get_settings()
    
    if not settings.database_url:
        logger.error("DATABASE_URL не настроен")
        raise ValueError("DATABASE_URL не найден в переменных окружения")
    
    db = Database(settings.database_url)
    await db.init_database()

async def close_db():
    """Закрытие соединения с базой данных"""
    global db
    if db:
        await db.close_pool()

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