import sys
from loguru import logger

def setup_logger():
    """Настройка логгера"""
    logger.remove()  # Удаляем стандартный обработчик
    
    # Добавляем вывод в консоль
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Добавляем запись в файл
    logger.add(
        "logs/trading_bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    return logger 