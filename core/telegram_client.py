from telethon import TelegramClient, events
from typing import Optional, Callable
from loguru import logger
import asyncio
import os

class TelegramBot:
    def __init__(self, api_id: str, api_hash: str, phone: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        # Используем более уникальное имя сессии
        session_name = f'trading_bot_{phone}_{api_id}'
        # Включаем режим userbot
        self.client = TelegramClient(session_name, api_id, api_hash, device_model="Trading Bot", system_version="1.0")
        self.message_handler: Optional[Callable] = None
        
    async def start(self):
        """Запуск бота"""
        # Проверяем существование файла сессии
        session_exists = os.path.exists(f'{self.client.session.filename}.session')
        
        if session_exists:
            logger.info("Найдена существующая сессия, пытаемся подключиться...")
            try:
                await self.client.connect()
                if await self.client.is_user_authorized():
                    logger.info("Успешно подключились к существующей сессии")
                    return
            except Exception as e:
                logger.warning(f"Не удалось использовать существующую сессию: {e}")
        
        logger.info("Создаем новую сессию...")
        # Используем userbot режим при авторизации
        await self.client.start(phone=self.phone, code_callback=None)
        logger.info("Telegram бот успешно запущен")
        
    async def stop(self):
        """Остановка бота"""
        await self.client.disconnect()
        logger.info("Telegram бот остановлен")
        
    def set_message_handler(self, handler: Callable):
        """Установка обработчика сообщений"""
        self.message_handler = handler
        
    async def monitor_channel(self, channel_username: str, interval: int = 5):
        """
        Мониторинг канала
        
        Args:
            channel_username: Имя канала (например, 'channel_name')
            interval: Интервал проверки в секундах
        """
        if not self.message_handler:
            raise ValueError("Обработчик сообщений не установлен")
            
        logger.info(f"Начинаем мониторинг канала {channel_username}")
        
        while True:
            try:
                # Получаем последние сообщения
                messages = await self.client.get_messages(channel_username, limit=1)
                
                if messages:
                    latest_message = messages[0]
                    # Передаем сообщение в обработчик
                    await self.message_handler(latest_message.text)
                    
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Ошибка при мониторинге канала: {e}")
                await asyncio.sleep(interval)
                
    async def run(self, channel_username: str, interval: int = 5):
        """Запуск бота с мониторингом канала"""
        await self.start()
        await self.monitor_channel(channel_username, interval) 