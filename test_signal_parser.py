from core.api_client import BybitClient
from strategies.signals import WolfixParser, SignalExecutor
from loguru import logger

def test_signal_parser():
    # Инициализация клиента, парсера и исполнителя
    client = BybitClient()
    parser = WolfixParser(client)
    executor = SignalExecutor(client)
    
    # Тестовый сигнал Wolfix
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
    logger.info(f"Источник сигнала: {signal_data['parser']}")
    
    # Проверка условий входа
    if executor.check_entry_conditions(signal_data):
        logger.info("Условия входа выполнены")
        # Выполнение сигнала (закомментировано для безопасности)
        executor.execute_signal(signal_data)  # Размер позиции будет рассчитан автоматически
    else:
        logger.info("Условия входа не выполнены")

if __name__ == "__main__":
    test_signal_parser() 