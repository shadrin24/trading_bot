import json
import time
from loguru import logger
from db.models import init_db
from core.api_client import BybitClient
from core.trade_manager import TradeManager
from core.logger import setup_logger
from strategies.moving_average import MovingAverageStrategy

def load_config(config_path: str = 'config/settings.json') -> dict:
    """Загрузка конфигурации"""
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    # Инициализация логгера
    logger = setup_logger()
    logger.info("Запуск торгового бота")
    
    # Инициализация базы данных
    init_db()
    logger.info("База данных инициализирована")
    
    # Загрузка конфигурации
    config = load_config()
    logger.info("Конфигурация загружена")
    
    # Инициализация компонентов
    api_client = BybitClient()
    trade_manager = TradeManager(api_client)
    strategy = MovingAverageStrategy(config)
    
    logger.info("Компоненты инициализированы")
    
    while True:
        try:
            # Получение данных
            klines = api_client.get_klines(
                symbol=config['symbol'],
                interval=config['timeframe'],
                limit=100
            )
            
            # Обновление стратегии
            for kline in klines['result']['list']:
                data = {
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                }
                strategy.update(data)
            
            # Генерация сигнала
            signal = strategy.generate_signal(data)
            
            if signal['action'] != 'hold':
                # Размещение ордера
                order = api_client.place_order(
                    symbol=config['symbol'],
                    side=signal['action'],
                    qty=signal['amount'],
                    price=signal['price']
                )
                
                # Логирование сделки
                trade_data = {
                    'symbol': config['symbol'],
                    'side': signal['action'],
                    'amount': signal['amount'],
                    'price': signal['price'],
                    'strategy': 'moving_average'
                }
                trade_manager.log_trade(trade_data)
                
                # Создание снимка баланса
                trade_manager.log_balance_snapshot()
            
            # Пауза между итерациями
            time.sleep(60)  # 1 минута
            
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(60)  # Пауза при ошибке

if __name__ == "__main__":
    main() 