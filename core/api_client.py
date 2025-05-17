import json
from typing import Dict, Any
from pybit.unified_trading import HTTP
from loguru import logger

class BybitClient:
    def __init__(self, config_path: str = 'config/keys.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.mode = 'mainnet'  # Используем mainnet для демо-трейдинга
        logger.info(f"Загружены ключи для режима: {self.mode}")
        self.client = self._init_client()
        # self._check_api_version()
    
    def _check_api_version(self):
        """Проверка версии API"""
        try:
            response = self.client.get_api_key_information()
            logger.info(f"Подключение к Bybit API v5 успешно установлено")
            logger.info(f"API Key информация: {response}")
        except Exception as e:
            logger.error(f"Ошибка при проверке версии API: {e}")
            raise
    
    def _init_client(self) -> HTTP:
        """Инициализация клиента Bybit"""
        try:
            api_key = self.config[self.mode]['api_key']
            api_secret = self.config[self.mode]['api_secret']
            
            logger.info(f"API Key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
            logger.info(f"API Secret: {api_secret[:5]}...{api_secret[-5:] if len(api_secret) > 10 else ''}")
            
            client = HTTP(
                testnet=False,
                demo=True,
                api_key=api_key,
                api_secret=api_secret
            )
            logger.info("Базовый URL для запросов: https://api-demo.bybit.com")
            return client
        except Exception as e:
            logger.error(f"Ошибка инициализации клиента Bybit: {e}")
            raise
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Dict[str, Any]:
        """Получение исторических данных"""
        try:
            response = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка получения исторических данных: {e}")
            raise
    
    def get_instrument_info(self, symbol: str) -> Dict[str, Any]:
        """Получение информации об инструменте"""
        try:
            response = self.client.get_instruments_info(
                category="linear",
                symbol=symbol
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка при получении информации об инструменте: {e}")
            raise
    
    def _convert_usdt_to_contracts(self, symbol: str, usdt_amount: float) -> float:
        """Конвертация USDT в количество контрактов"""
        try:
            # Получаем информацию об инструменте
            instrument_info = self.get_instrument_info(symbol)
            min_qty = float(instrument_info['result']['list'][0]['lotSizeFilter']['minOrderQty'])
            qty_step = float(instrument_info['result']['list'][0]['lotSizeFilter']['qtyStep'])
            logger.info(f"Минимальный размер ордера для {symbol}: {min_qty}, шаг: {qty_step}")
            
            # Получаем текущую цену
            klines = self.get_klines(symbol=symbol, interval="1", limit=1)
            current_price = float(klines['result']['list'][0][4])
            logger.info(f"Текущая цена {symbol}: {current_price}")
            
            # Рассчитываем количество контрактов
            contracts = usdt_amount / current_price
            logger.info(f"Рассчитанное количество контрактов до округления: {contracts}")
            
            # Проверяем минимальный размер
            if contracts < min_qty:
                logger.warning(f"Количество контрактов ({contracts}) меньше минимального ({min_qty}). Увеличиваем до минимума.")
                contracts = min_qty
            
            # Округляем до шага
            contracts = round(contracts / qty_step) * qty_step
            logger.info(f"Количество контрактов после округления: {contracts}")
            
            # Форматируем число с фиксированным количеством знаков после запятой
            formatted_contracts = float(f"{contracts:.3f}")
            logger.info(f"Отформатированное количество контрактов: {formatted_contracts}")
            
            return formatted_contracts
        except Exception as e:
            logger.error(f"Ошибка при конвертации USDT в контракты: {e}")
            raise
    
    def place_order(self, symbol: str, side: str, qty: float, take_profit: bool = False,
                   tp_trigger_price: float = None, tp_quantity_percentage: float = None,
                   stop_loss: bool = False, sl_trigger_price: float = None, sl_quantity_percentage: float = None) -> Dict:
        """Размещение ордера"""
        try:
            # Конвертируем USDT в контракты
            contracts = self._convert_usdt_to_contracts(symbol, qty)
            contracts_str = f"{contracts:.3f}"
            
            # Форматируем сторону ордера (первая буква заглавная)
            side = side.capitalize()
            
            # Базовые параметры ордера
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "qty": contracts_str,
                "orderType": "MARKET",
                "positionIdx": 0,
                "timeInForce": "GTC",
                "tpslMode": "Full"  # Изменено на Full
            }
            
            # Добавляем тейк-профит если указан
            if take_profit and tp_trigger_price:
                # Получаем информацию об инструменте для округления
                instrument_info = self.get_instrument_info(symbol)
                min_qty = float(instrument_info['minOrderQty'])
                qty_step = float(instrument_info['qtyStep'])
                
                # Рассчитываем размер в контрактах
                tp_contracts = (contracts * tp_quantity_percentage / 100)
                # Округляем до шага
                tp_contracts = round(tp_contracts / qty_step) * qty_step
                # Проверяем минимальный размер
                if tp_contracts < min_qty:
                    logger.warning(f"Размер тейк-профита {tp_contracts} меньше минимального {min_qty}, увеличиваем до минимума")
                    tp_contracts = min_qty
                
                tp_contracts_str = f"{tp_contracts:.3f}"
                logger.info(f"Конвертация {tp_quantity_percentage}% в {tp_contracts_str} контрактов для тейк-профита")
                
                params.update({
                    "takeProfit": str(tp_trigger_price),
                    "tpTriggerBy": "LastPrice",
                    "tpSize": tp_contracts_str
                })
            
            # Добавляем стоп-лосс если указан
            if stop_loss and sl_trigger_price:
                params.update({
                    "stopLoss": str(sl_trigger_price),
                    "slTriggerBy": "LastPrice"
                })
            
            logger.info(f"Параметры ордера: {params}")
            
            response = self.client.place_order(**params)
            if response['retCode'] == 0:
                logger.info(f"Ордер успешно размещен: {response['result']}")
                return response['result']
            else:
                error_msg = f"Ошибка размещения ордера: {response['retMsg']} (ErrCode: {response['retCode']})"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Ошибка при размещении ордера: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Получение баланса"""
        try:
            response = self.client.get_wallet_balance(
                accountType="UNIFIED"
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            raise
    
    def place_take_profit(self, symbol: str, tp_trigger_price: float, tp_quantity_percentage: int, total_position_size: float) -> Dict[str, Any]:
        """Добавление тейк-профита к существующей позиции"""
        try:
            # Получаем информацию об инструменте
            instrument_info = self.get_instrument_info(symbol)
            qty_step = float(instrument_info['result']['list'][0]['lotSizeFilter']['qtyStep'])
            
            # Рассчитываем количество контрактов для тейк-профита
            tp_contracts = (total_position_size * tp_quantity_percentage / 100)
            # Округляем до шага
            tp_contracts = round(tp_contracts / qty_step) * qty_step
            # Форматируем число
            tp_contracts_str = f"{tp_contracts:.3f}"
            
            logger.info(f"Конвертация {tp_quantity_percentage}% в {tp_contracts_str} контрактов для тейк-профита")
            
            params = {
                "category": "linear",
                "symbol": symbol,
                "takeProfit": str(tp_trigger_price),
                "tpTriggerBy": "LastPrice",
                "tpSize": tp_contracts_str,  # Используем tpSize вместо qty
                "tpslMode": "Full" if tp_quantity_percentage == 100 else "Partial"  # Full для TP3, Partial для остальных
            }
            
            logger.info(f"Добавление тейк-профита: {params}")
            response = self.client.set_trading_stop(**params)
            return response
        except Exception as e:
            logger.error(f"Ошибка добавления тейк-профита: {e}")
            raise 