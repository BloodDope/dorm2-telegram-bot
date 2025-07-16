# 🚀 Миграция на Oracle Cloud Always Free

## Подготовка к миграции (пока Railway работает)

### 1. Создание аккаунта Oracle Cloud
- Перейти на https://cloud.oracle.com/free
- Создать аккаунт (нужна карта для верификации, деньги НЕ спишут)
- Получить Always Free tier

### 2. Создание VM инстанса
```bash
# Конфигурация для вашего бота:
- ОС: Ubuntu 22.04
- Shape: VM.Standard.E2.1.Micro (Always Free)
- RAM: 1GB
- vCPU: 1
- Диск: 50GB (бесплатно)
```

### 3. Настройка сервера
```bash
# Подключение по SSH
ssh ubuntu@your_oracle_ip

# Установка зависимостей
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git supervisor -y

# Создание пользователя для бота
sudo useradd -m -s /bin/bash botuser
sudo usermod -aG sudo botuser
```

### 4. Деплой бота
```bash
# Переключение на пользователя бота
sudo su - botuser

# Клонирование репозитория
git clone https://github.com/BloodDope/dorm2-telegram-bot.git
cd dorm2-telegram-bot

# Установка зависимостей
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создание .env файла
nano .env
# Добавить все переменные как в Railway
```

### 5. Настройка автозапуска
```bash
# Создание systemd service
sudo nano /etc/systemd/system/tgbot.service

[Unit]
Description=Telegram Bot for Dormitory
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/dorm2-telegram-bot
Environment=PATH=/home/botuser/dorm2-telegram-bot/venv/bin
ExecStart=/home/botuser/dorm2-telegram-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable tgbot
sudo systemctl start tgbot
```

## Результат
✅ Бот работает 24/7 навсегда бесплатно
✅ Никаких временных ограничений
✅ Профессиональная инфраструктура Oracle 