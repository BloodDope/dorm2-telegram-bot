#!/usr/bin/env python3
"""
Тест для проверки переменных окружения в Railway
"""
import os

def test_environment_variables():
    """Проверяет все необходимые переменные окружения"""
    required_vars = {
        'BOT_TOKEN': 'Токен Telegram бота',
        'ADMIN_IDS': 'ID администраторов',
        'LOG_LEVEL': 'Уровень логирования',
        'ENVIRONMENT': 'Режим работы'
    }
    
    print("🔍 Проверка переменных окружения...")
    print("=" * 50)
    
    all_good = True
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Маскируем токен для безопасности
            if var_name == 'BOT_TOKEN':
                masked_value = value[:10] + "..." + value[-5:] if len(value) > 15 else "***"
                print(f"✅ {var_name}: {masked_value}")
            else:
                print(f"✅ {var_name}: {value}")
        else:
            print(f"❌ {var_name}: НЕ НАЙДЕНА ({description})")
            all_good = False
    
    print("=" * 50)
    
    if all_good:
        print("🎉 Все переменные найдены! Бот должен работать.")
    else:
        print("⚠️  Найдены проблемы с переменными окружения!")
        print("📋 Что делать:")
        print("1. Перейдите в Railway Variables")
        print("2. Добавьте недостающие переменные")
        print("3. Нажмите Redeploy")
    
    return all_good

if __name__ == "__main__":
    test_environment_variables() 