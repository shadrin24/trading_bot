import json
from typing import Dict, Any
from pybit.unified_trading import HTTP
from loguru import logger

class BybitClient:
    def __init__(self, config_path: str = 'config/keys.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.mode = 'testnet'  # По умолчанию используем тестовый режим
        self.client = self._init_client()
    
    def _init_client(self) -> HTTP:
        """Инициализация клиента Bybit"""
        try:
            api_key = self.config[self.mode]['api_key']
            api_secret = self.config[self.mode]['api_secret']
            
            return HTTP(
                testnet=self.mode == 'testnet',
                api_key=api_key,
                api_secret=api_secret
            )
        except Exception as e:
            logger.error(f"Ошибка инициализации клиента Bybit: {e}")
            raise
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Dict[str, Any]:
        """Получение исторических данных"""
        try:
            response = self.client.get_kline(
                category="spot",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка получения исторических данных: {e}")
            raise
    
    def place_order(self, symbol: str, side: str, qty: float, price: float = None) -> Dict[str, Any]:
        """Размещение ордера"""
        try:
            params = {
                "category": "spot",
                "symbol": symbol,
                "side": side.upper(),
                "qty": str(qty),
                "orderType": "LIMIT" if price else "MARKET"
            }
            
            if price:
                params["price"] = str(price)
            
            response = self.client.place_order(**params)
            return response
        except Exception as e:
            logger.error(f"Ошибка размещения ордера: {e}")
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