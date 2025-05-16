import pandas as pd
import numpy as np
from typing import Dict, Any
from .base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sma_period = config.get('sma_period', 20)
        self.position_size = config.get('position_size', 0.001)
        self.prices = []
        self.current_position = None
    
    def update(self, data: Dict[str, Any]) -> None:
        """Обновляет историю цен"""
        self.prices.append(float(data['close']))
        if len(self.prices) > self.sma_period:
            self.prices.pop(0)
    
    def generate_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует сигнал на основе SMA"""
        if len(self.prices) < self.sma_period:
            return {'action': 'hold', 'price': float(data['close']), 'amount': 0}
        
        current_price = float(data['close'])
        sma = np.mean(self.prices)
        
        signal = {
            'price': current_price,
            'amount': self.position_size
        }
        
        if current_price > sma and not self.current_position:
            signal['action'] = 'buy'
            self.current_position = 'long'
        elif current_price < sma and self.current_position == 'long':
            signal['action'] = 'sell'
            self.current_position = None
        else:
            signal['action'] = 'hold'
            signal['amount'] = 0
        
        return signal 