from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.api_client import BybitClient

class BaseSignalParser(ABC):
    def __init__(self, api_client: BybitClient):
        self.api_client = api_client
    
    @abstractmethod
    def parse_signal(self, message: str) -> Optional[Dict[str, Any]]:
        """Парсинг торгового сигнала из сообщения"""
        pass
    
    @abstractmethod
    def get_parser_name(self) -> str:
        """Возвращает название парсера"""
        pass 