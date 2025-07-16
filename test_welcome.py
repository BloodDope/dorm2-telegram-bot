from config.content import WELCOME_MESSAGE

# Тестируем форматирование
try:
    result = WELCOME_MESSAGE.format(first_name="Тест")
    print("✅ Форматирование работает:")
    print(result[:200] + "...")
except Exception as e:
    print("❌ Ошибка форматирования:", e)
