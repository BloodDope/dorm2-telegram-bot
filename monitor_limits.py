#!/usr/bin/env python3
"""
Мониторинг лимитов использования бесплатных платформ
"""
import requests
import datetime

def check_railway_hours():
    """Проверка оставшихся часов на Railway"""
    # API вызов к Railway (нужен токен)
    # Возвращает оставшиеся часы
    pass

def send_alert_to_admin(platform, hours_left):
    """Отправка уведомления администратору через Telegram"""
    bot_token = "YOUR_BOT_TOKEN"
    admin_id = "570918216"
    
    message = f"⚠️ Внимание! На {platform} осталось {hours_left} часов"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": admin_id,
        "text": message
    }
    
    requests.post(url, data=data)

def main():
    """Основная функция мониторинга"""
    # Проверяем лимиты на всех платформах
    railway_hours = check_railway_hours()
    
    # Отправляем уведомления если мало часов
    if railway_hours < 50:  # Меньше 50 часов
        send_alert_to_admin("Railway", railway_hours)

if __name__ == "__main__":
    main() 