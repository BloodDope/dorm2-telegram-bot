import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Проверяем переменные
print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("ADMIN_IDS:", os.getenv("ADMIN_IDS"))
print("Current directory:", os.getcwd())
print(".env file exists:", os.path.exists(".env"))
