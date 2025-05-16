from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseStrategy(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.symbol = config.get('symbol', 'BTCUSDT')
        self.timeframe = config.get('timeframe', '1h')
    
    @abstractmethod
    def generate_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует торговый сигнал на основе входных данных
        
        Returns:
            Dict[str, Any]: Словарь с сигналом
            {
                'action': 'buy' | 'sell' | 'hold',
                'price': float,
                'amount': float
            }
        """
        pass
    
    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Обновляет внутреннее состояние стратегии
        """
        pass 