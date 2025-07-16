#!/usr/bin/env python3
"""
Скрипт для автоматической ротации деплоя между платформами
"""
import datetime
import subprocess
import os

def get_current_platform():
    """Определяет на какой платформе должен работать бот сегодня"""
    today = datetime.date.today()
    day = today.day
    
    if day <= 20:
        return "railway"
    else:
        return "render"

def deploy_to_railway():
    """Деплой на Railway"""
    print("🚀 Deploying to Railway...")
    # Команды для деплоя на Railway
    subprocess.run(["railway", "deploy"])

def deploy_to_render():
    """Деплой на Render"""
    print("🚀 Deploying to Render...")
    # Команды для деплоя на Render
    subprocess.run(["git", "push", "render", "main"])

def stop_platform(platform):
    """Останавливает бота на указанной платформе"""
    if platform == "railway":
        subprocess.run(["railway", "down"])
    elif platform == "render":
        # Render останавливается автоматически
        pass

if __name__ == "__main__":
    current_platform = get_current_platform()
    
    print(f"📅 Сегодня: {datetime.date.today()}")
    print(f"🎯 Активная платформа: {current_platform}")
    
    if current_platform == "railway":
        deploy_to_railway()
        stop_platform("render")
    else:
        deploy_to_render()
        stop_platform("railway")
    
    print("✅ Ротация завершена!") 