import re
from typing import Dict, Any, Optional
from loguru import logger
from core.api_client import BybitClient
from .base_parser import BaseSignalParser

class WolfixParser(BaseSignalParser):
    def __init__(self, api_client: BybitClient):
        super().__init__(api_client)
        
    def get_parser_name(self) -> str:
        return "Wolfix"
        
    def parse_signal(self, message: str) -> Optional[Dict[str, Any]]:
        """Парсинг торгового сигнала из сообщения Wolfix"""
        try:
            logger.debug(f"Начинаем парсинг сигнала Wolfix: {message}")
            
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
                'leverage': leverage,
                'parser': self.get_parser_name()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге сигнала Wolfix: {e}")
            return None 