from core.api_client import BybitClient
from strategies.signal_parser import SignalParser
from loguru import logger

def test_signal_parser():
    # Инициализация клиента и парсера
    client = BybitClient()
    parser = SignalParser(client)
    
    # Тестовый сигнал
    test_signal = """🔔CRYPTO VIP SIGNAL (https://wolfxsignals.com/plans-lp/)🔔

ETH/USDT 📉 BUY 

🔹Entry zone: 2480-2500 

💰TP1 2600
💰TP2 2700
💰TP3 2800
🚫SL 2400

〽️Leverage 10x"""
    
    # Парсинг сигнала
    signal_data = parser.parse_signal(test_signal)
    if not signal_data:
        logger.error("Не удалось распарсить сигнал")
        return
        
    logger.info(f"Распарсенный сигнал: {signal_data}")
    
    # Проверка условий входа
    if parser.check_entry_conditions(signal_data):
        logger.info("Условия входа выполнены")
        # Выполнение сигнала (закомментировано для безопасности)
        parser.execute_signal(signal_data)  # Размер позиции будет рассчитан автоматически
    else:
        logger.info("Условия входа не выполнены")

if __name__ == "__main__":
    test_signal_parser() 