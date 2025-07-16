"""
HTTP endpoint для предотвращения автосна на Render.com
"""
from aiohttp import web
import asyncio
import logging

async def health_check(request):
    """Простой endpoint для проверки здоровья"""
    return web.json_response({
        "status": "ok", 
        "message": "Bot is alive"
    })

async def create_web_server():
    """Создаем веб-сервер для keep-alive"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    return app

async def start_web_server(app, port=8000):
    """Запускаем веб-сервер"""
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info(f"Web server started on port {port}")
    return runner 