from typing import Dict, Any
from loguru import logger
from core.api_client import BybitClient

class SignalExecutor:
    def __init__(self, api_client: BybitClient):
        self.api_client = api_client
        
    def check_entry_conditions(self, signal: Dict[str, Any]) -> bool:
        """Проверка условий для входа в позицию"""
        try:
            # Получаем текущую цену
            klines = self.api_client.get_klines(
                symbol=signal['symbol'],
                interval="1",
                limit=1
            )
            current_price = float(klines['result']['list'][0][4])
            
            # Проверяем, находится ли цена в зоне входа
            if signal['entry_low'] <= current_price <= signal['entry_high']:
                return True
                
            # Проверяем дополнительные условия
            if signal['side'] == 'SELL':
                # Для продажи: цена должна быть выше TP1 на 0.2%
                min_price = signal['tp1'] * 1.002
                return current_price >= min_price
            else:
                # Для покупки: цена должна быть ниже TP1 на 0.2%
                max_price = signal['tp1'] * 0.998
                return current_price <= max_price
                
        except Exception as e:
            logger.error(f"Ошибка при проверке условий входа: {e}")
            return False
            
    def execute_signal(self, signal: Dict[str, Any]) -> None:
        """Выполнение торгового сигнала"""
        try:
            symbol = signal['symbol']
            side = signal['side']
            entry_price = (signal['entry_high'] + signal['entry_low']) / 2  # Используем среднюю цену зоны входа
            sl_price = signal['sl']
            tp_prices = [signal['tp1'], signal['tp2'], signal['tp3']]
            
            # Получаем баланс
            balance_data = self.api_client.get_balance()
            available_balance = float(balance_data['result']['list'][0]['totalAvailableBalance'])
            logger.info(f"Доступный баланс: {available_balance} USDT")
            
            # Рассчитываем размер позиции (1% от баланса)
            position_size = available_balance * 0.01
            logger.info(f"Размер позиции: {position_size} USDT")
            
            # Конвертируем размер позиции в контракты
            position_contracts = self.api_client._convert_usdt_to_contracts(symbol, position_size)
            logger.info(f"Размер позиции в контрактах: {position_contracts}")
            
            # Размещаем основной ордер (рыночный) только со стоп-лоссом
            logger.info(f"Размещение основного ордера: {side} {symbol}")
            logger.info(f"Тейк-профиты: TP1={tp_prices[0]} (30%), TP2={tp_prices[1]} (30%), TP3={tp_prices[2]} (100%)")
            logger.info(f"Стоп-лосс: {sl_price} (100%)")
            
            self.api_client.place_order(
                symbol=symbol,
                side=side,
                qty=position_size,
                take_profit=False,  # Убираем тейк-профит из основного ордера
                stop_loss=True,
                sl_trigger_price=sl_price,
                sl_quantity_percentage=100  # 100% для стоп-лосса
            )
            
            # Добавляем первый тейк-профит
            self.api_client.place_take_profit(
                symbol=symbol,
                tp_trigger_price=tp_prices[0],
                tp_quantity_percentage=30,  # 30% для первого тейк-профита
                total_position_size=position_contracts
            )
            
            # Добавляем второй тейк-профит
            self.api_client.place_take_profit(
                symbol=symbol,
                tp_trigger_price=tp_prices[1],
                tp_quantity_percentage=30,  # 30% для второго тейк-профита
                total_position_size=position_contracts
            )
            
            # Добавляем третий тейк-профит на всю позицию
            self.api_client.place_take_profit(
                symbol=symbol,
                tp_trigger_price=tp_prices[2],
                tp_quantity_percentage=100,  # 100% для третьего тейк-профита
                total_position_size=position_contracts
            )
            
            logger.info("Сигнал успешно выполнен")
            
        except Exception as e:
            logger.error(f"Ошибка выполнения сигнала: {e}")
            raise 