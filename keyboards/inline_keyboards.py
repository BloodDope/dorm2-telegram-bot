from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config.content import FLOOR_NUMBERS, VIDEO_CATEGORIES

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [InlineKeyboardButton(text="📢 Официальный канал общежития", callback_data="official_channel")],
        [InlineKeyboardButton(text="💡 Студенческий Совет", callback_data="student_council")],
        [InlineKeyboardButton(text="🗣 Чат твоего этажа", callback_data="floor_chats")],
        [InlineKeyboardButton(text="👥 Общий чат общежития", callback_data="general_chat")],
        [InlineKeyboardButton(text="📚 Сайт с ГАЙДОМ", callback_data="guide_website")],
        [InlineKeyboardButton(text="🎬 Видео-гайд", callback_data="video_guide")],
        [InlineKeyboardButton(text="📞 Важные контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="📝 Обратная связь", callback_data="feedback")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Кнопки назад и в главное меню"""
    keyboard = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data)],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_student_council_keyboard() -> InlineKeyboardMarkup:
    """Меню студенческого совета"""
    keyboard = [
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_floor_chats_keyboard() -> InlineKeyboardMarkup:
    """Выбор группы этажей для чата"""
    keyboard = [
        [InlineKeyboardButton(text="❤️ 2-3 этажи", url="https://t.me/+PpzqjAhVIaZhODVi")],
        [InlineKeyboardButton(text="🧡 4-5 этажи", url="https://t.me/+71VFxPGs19tmZWI6")],
        [InlineKeyboardButton(text="💛 6-7 этажи", url="https://t.me/+ZrlWgxCdMYg5MDJi")],
        [InlineKeyboardButton(text="💚 8-9 этажи", url="https://t.me/+nctBTwVabnIxZjFi")],
        [InlineKeyboardButton(text="🩵 10-11 этажи", url="https://t.me/+f32Cs8l5nJQ0NjVi")],
        [InlineKeyboardButton(text="💙 12-13 этажи", url="https://t.me/+sLFbAwIKAWQ1ZTBi")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_video_categories_keyboard() -> InlineKeyboardMarkup:
    """Категории видео-гайдов"""
    keyboard = []
    
    for category_id, category_info in VIDEO_CATEGORIES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=category_info["name"],
                callback_data=f"video_category_{category_id}"
            )
        ])
    
    # Кнопки навигации
    keyboard.extend([
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_contacts_keyboard() -> InlineKeyboardMarkup:
    """Категории контактов"""
    keyboard = [
        [InlineKeyboardButton(text="🏢 Администрация общежития", callback_data="contacts_admin")],
        [InlineKeyboardButton(text="🚨 Экстренные службы", callback_data="contacts_emergency")],
        [InlineKeyboardButton(text="🔧 Техническая поддержка", callback_data="contacts_technical")],
        [InlineKeyboardButton(text="💡 Студенческий совет", callback_data="contacts_council")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_feedback_type_keyboard() -> InlineKeyboardMarkup:
    """Типы обратной связи"""
    keyboard = [
        [InlineKeyboardButton(text="💡 Предложение по улучшению", callback_data="feedback_suggestion")],
        [InlineKeyboardButton(text="🐛 Сообщить об ошибке", callback_data="feedback_bug")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="feedback_question")],
        [InlineKeyboardButton(text="💬 Общий отзыв", callback_data="feedback_general")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Административные клавиатуры

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Панель администратора"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Редактировать контент", callback_data="admin_edit_content")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📨 Массовая рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🎬 Управление видео", callback_data="admin_videos")],
        [InlineKeyboardButton(text="📞 Обновить контакты", callback_data="admin_contacts")],
        [InlineKeyboardButton(text="💬 Обратная связь", callback_data="admin_feedback")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_content_keyboard() -> InlineKeyboardMarkup:
    """Редактирование контента"""
    keyboard = [
        [InlineKeyboardButton(text="📢 Ссылка на канал", callback_data="edit_channel_link")],
        [InlineKeyboardButton(text="👥 Ссылка на общий чат", callback_data="edit_general_chat_link")],
        [InlineKeyboardButton(text="📚 Ссылка на сайт-гайд", callback_data="edit_guide_link")],
        [InlineKeyboardButton(text="🗣 Ссылки на чаты этажей", callback_data="edit_floor_links")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="edit_contacts_text")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Статистика - дополнительные опции"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Обновить статистику", callback_data="refresh_stats")],
        [InlineKeyboardButton(text="📈 Экспорт данных", callback_data="export_stats")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение массовой рассылки"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Отправить", callback_data="broadcast_confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="broadcast_cancel")],
        [InlineKeyboardButton(text="✏️ Изменить", callback_data="broadcast_edit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_video_management_keyboard() -> InlineKeyboardMarkup:
    """Управление видео"""
    keyboard = []
    
    for category_id, category_info in VIDEO_CATEGORIES.items():
        keyboard.append([
            InlineKeyboardButton(
                text=f"📹 {category_info['name']}",
                callback_data=f"admin_video_{category_id}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton(text="➕ Добавить новое видео", callback_data="admin_add_video")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Reply клавиатуры

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для первого запуска бота"""
    keyboard = [
        [KeyboardButton(text="🚀 Начать")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите 'Начать' чтобы открыть меню бота"
    )

def remove_keyboard() -> ReplyKeyboardMarkup:
    """Убирает Reply клавиатуру"""
    return ReplyKeyboardMarkup(
        keyboard=[], 
        resize_keyboard=True,
        remove_keyboard=True
    ) 