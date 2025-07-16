from aiogram import Dispatcher
from . import basic_handlers, callback_handlers, admin_handlers, feedback_handlers

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Регистрируем обработчики в правильном порядке
    # Feedback handlers должны быть перед basic_handlers, чтобы обрабатывать состояния
    feedback_handlers.register_feedback_handlers(dp)
    basic_handlers.register_basic_handlers(dp)
    callback_handlers.register_callback_handlers(dp)
    admin_handlers.register_admin_handlers(dp) 