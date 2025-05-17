import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)

from core.api_client import BybitClient
from loguru import logger
from core.logger import setup_logger

def test_connection():
    # Инициализация логгера
    logger = setup_logger()
    logger.info("Начинаем тест подключения к Bybit")
    
    try:
        # Инициализация клиента
        client = BybitClient()
        
        # Проверка баланса
        logger.info("Проверяем баланс...")
        balance = client.get_balance()
        logger.info(f"Баланс: {balance}")
        
        # Параметры ордера
        symbol = "ETHUSDT"
        side = "Buy"
        qty = 50  # Размер позиции в USD
        price = 2300  # Цена входа
        leverage = 15  # Плечо
        
        # Установка плеча
        logger.info(f"Устанавливаем плечо {leverage}x для {symbol}")
        try:
            client.client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
        except Exception as e:
            if "110043" in str(e):
                logger.info("Плечо уже установлено на нужное значение, продолжаем работу.")
            else:
                logger.error(f"Ошибка при установке плеча: {e}")
                raise
        
        # Размещение лимитного ордера
        logger.info(f"Размещаем лимитный ордер на покупку {symbol}")
        order = client.place_order(
            symbol=symbol,
            side=side,
            qty=qty,
            price=price
        )
        
        logger.info(f"Ордер успешно размещен: {order}")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
        raise

if __name__ == "__main__":
    test_connection() 