import re
from typing import Dict, Any, Optional, Tuple
from loguru import logger
from core.api_client import BybitClient

class SignalParser:
    def __init__(self, api_client: BybitClient):
        self.api_client = api_client
        
    def parse_signal(self, message: str) -> Optional[Dict[str, Any]]:
        """Парсинг торгового сигнала из сообщения"""
        try:
            logger.debug(f"Начинаем парсинг сигнала: {message}")
            
            # Извлекаем торговую пару и направление
            pair_match = re.search(r'([A-Z]+/[A-Z]+)\s*[📈📉]\s*(BUY|SELL)', message)
            if not pair_match:
                logger.error("Не удалось найти торговую пару и направление")
                return None
                
            symbol = pair_match.group(1).replace('/', '')
            side = pair_match.group(2)
            logger.debug(f"Найдена торговая пара: {symbol}, направление: {side}")
            
            # Извлекаем зону входа
            entry_match = re.search(r'Entry zone:\s*(\d+\.?\d*)-(\d+\.?\d*)', message)
            if not entry_match:
                logger.error("Не удалось найти зону входа")
                logger.debug(f"Текст для поиска зоны входа: {message}")
                return None
                
            entry_high = float(entry_match.group(1))
            entry_low = float(entry_match.group(2))
            logger.debug(f"Найдена зона входа: {entry_low}-{entry_high}")
            
            # Извлекаем тейк-профиты
            tp_matches = re.findall(r'TP\d+\s*(\d+\.?\d*)', message)
            logger.debug(f"Найденные тейк-профиты: {tp_matches}")
            
            if len(tp_matches) != 3:
                logger.error(f"Не удалось найти все тейк-профиты. Найдено: {len(tp_matches)}")
                logger.debug(f"Текст для поиска тейк-профитов: {message}")
                return None
                
            tp1, tp2, tp3 = map(float, tp_matches)
            logger.debug(f"Распарсенные тейк-профиты: TP1={tp1}, TP2={tp2}, TP3={tp3}")
            
            # Извлекаем стоп-лосс
            sl_match = re.search(r'SL\s*(\d+\.?\d*)', message)
            if not sl_match:
                logger.error("Не удалось найти стоп-лосс")
                logger.debug(f"Текст для поиска стоп-лосса: {message}")
                return None
                
            sl = float(sl_match.group(1))
            logger.debug(f"Найден стоп-лосс: {sl}")
            
            # Извлекаем плечо
            leverage_match = re.search(r'Leverage\s*(\d+)x', message)
            if not leverage_match:
                logger.error("Не удалось найти плечо")
                logger.debug(f"Текст для поиска плеча: {message}")
                return None
                
            leverage = int(leverage_match.group(1))
            logger.debug(f"Найдено плечо: {leverage}x")
            
            return {
                'symbol': symbol,
                'side': side,
                'entry_high': entry_high,
                'entry_low': entry_low,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
                'sl': sl,
                'leverage': leverage
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге сигнала: {e}")
            return None
            
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