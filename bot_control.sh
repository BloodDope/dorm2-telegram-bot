#!/bin/bash

BOT_DIR="/Users/pavelklyuchuk/Desktop/tgbot"
PID_FILE="$BOT_DIR/bot.pid"
LOG_FILE="$BOT_DIR/logs/bot_daemon.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Бот уже запущен (PID: $PID)"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi
        
        echo "Запускаю бота..."
        cd "$BOT_DIR"
        nohup .venv/bin/python main.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        echo "Бот запущен! PID: $(cat $PID_FILE)"
        echo "Логи: $LOG_FILE"
        ;;
    
    stop)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Останавливаю бота (PID: $PID)..."
                kill "$PID"
                rm -f "$PID_FILE"
                echo "Бот остановлен"
            else
                echo "Процесс бота не найден"
                rm -f "$PID_FILE"
            fi
        else
            echo "PID файл не найден. Бот не запущен?"
        fi
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Бот работает (PID: $PID)"
            else
                echo "❌ PID файл есть, но процесс не найден"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Бот не запущен"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        tail -f "$LOG_FILE"
        ;;
    
    *)
        echo "Использование: $0 {start|stop|status|restart|logs}"
        echo "  start   - Запустить бота"
        echo "  stop    - Остановить бота"
        echo "  status  - Проверить статус"
        echo "  restart - Перезапустить бота"
        echo "  logs    - Показать логи в реальном времени"
        ;;
esac
