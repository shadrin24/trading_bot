import asyncio
import json
from typing import Optional
from loguru import logger
from core.api_client import BybitClient
from core.telegram_client import TelegramBot
from .wolfix_parser import WolfixParser
from .signal_executor import SignalExecutor

class WolfixBot:
    def __init__(self, 
                 telegram_api_id: str,
                 telegram_api_hash: str,
                 telegram_phone: str,
                 channel_username: str,
                 check_interval: int = 5):
        """
        Инициализация бота Wolfix
        
        Args:
            telegram_api_id: ID API Telegram
            telegram_api_hash: Hash API Telegram
            telegram_phone: Номер телефона для авторизации
            channel_username: Имя канала для мониторинга
            check_interval: Интервал проверки сообщений в секундах
        """
        # Инициализация клиентов
        self.api_client = BybitClient()
        self.parser = WolfixParser(self.api_client)
        self.executor = SignalExecutor(self.api_client)
        
        # Инициализация Telegram бота
        self.telegram_bot = TelegramBot(
            api_id=telegram_api_id,
            api_hash=telegram_api_hash,
            phone=telegram_phone
        )
        
        self.channel_username = channel_username
        self.check_interval = check_interval
        self.last_processed_message: Optional[str] = None
        
    async def handle_message(self, message: str):
        """Обработка сообщения из Telegram"""
        # Проверяем, не обрабатывали ли мы уже это сообщение
        if message == self.last_processed_message:
            return
            
        logger.info("Получено новое сообщение")
        self.last_processed_message = message
        
        # Парсим сигнал
        signal_data = self.parser.parse_signal(message)
        if not signal_data:
            logger.info("Сообщение не является торговым сигналом")
            return
            
        logger.info(f"Распарсенный сигнал: {signal_data}")
        logger.info(f"Источник сигнала: {signal_data['parser']}")
        
        # Проверяем условия входа
        if self.executor.check_entry_conditions(signal_data):
            logger.info("Условия входа выполнены")
            # Выполняем сигнал
            self.executor.execute_signal(signal_data)
        else:
            logger.info("Условия входа не выполнены")
            
    async def run(self):
        """Запуск бота"""
        # Устанавливаем обработчик сообщений
        self.telegram_bot.set_message_handler(self.handle_message)
        
        try:
            # Запускаем бота
            await self.telegram_bot.run(
                channel_username=self.channel_username,
                interval=self.check_interval
            )
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        finally:
            # Останавливаем бота
            await self.telegram_bot.stop()
            
def run_wolfix_bot(telegram_api_id: str,
                   telegram_api_hash: str,
                   telegram_phone: str,
                   channel_username: str,
                   check_interval: int = 5):
    """
    Запуск бота Wolfix
    
    Args:
        telegram_api_id: ID API Telegram
        telegram_api_hash: Hash API Telegram
        telegram_phone: Номер телефона для авторизации
        channel_username: Имя канала для мониторинга
        check_interval: Интервал проверки сообщений в секундах
    """
    bot = WolfixBot(
        telegram_api_id=telegram_api_id,
        telegram_api_hash=telegram_api_hash,
        telegram_phone=telegram_phone,
        channel_username=channel_username,
        check_interval=check_interval
    )
    
    # Запускаем бота в асинхронном режиме
    asyncio.run(bot.run())

def main():
    """Запуск бота с параметрами из конфигурации"""
    # Загружаем конфигурацию
    with open('config/keys.json', 'r') as f:
        config = json.load(f)
    telegram_config = config['telegram']
    
    # Запускаем бота
    run_wolfix_bot(
        telegram_api_id=telegram_config['api_id'],
        telegram_api_hash=telegram_config['api_hash'],
        telegram_phone=telegram_config['telegram_phone'],
        channel_username=telegram_config['channel_username'],
        check_interval=telegram_config['check_interval']
    )

if __name__ == "__main__":
    main() 