from typing import Dict, Any
from datetime import datetime
from loguru import logger
from db.models import Trade, BalanceSnapshot, Session
from core.api_client import BybitClient

class TradeManager:
    def __init__(self, api_client: BybitClient):
        self.api_client = api_client
        self.session = Session()
    
    def log_trade(self, trade_data: Dict[str, Any]) -> None:
        """Логирование сделки в БД"""
        try:
            trade = Trade(
                symbol=trade_data['symbol'],
                side=trade_data['side'],
                amount=trade_data['amount'],
                price=trade_data['price'],
                fee=trade_data.get('fee', 0.0),
                strategy=trade_data.get('strategy', 'unknown'),
                timestamp=datetime.utcnow()
            )
            self.session.add(trade)
            self.session.commit()
            logger.info(f"Сделка залогирована: {trade_data}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка логирования сделки: {e}")
            raise
    
    def log_balance_snapshot(self) -> None:
        """Создание снимка баланса"""
        try:
            balance_data = self.api_client.get_balance()
            
            snapshot = BalanceSnapshot(
                balance=float(balance_data['totalWalletBalance']),
                equity=float(balance_data['totalEquity']),
                margin=float(balance_data['totalInitialMargin']),
                free_margin=float(balance_data['availableToWithdraw'])
            )
            
            self.session.add(snapshot)
            self.session.commit()
            logger.info("Снимок баланса создан")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка создания снимка баланса: {e}")
            raise
    
    def calculate_pnl(self, trade_id: int) -> float:
        """Расчет PnL для сделки"""
        try:
            trade = self.session.query(Trade).get(trade_id)
            if not trade:
                raise ValueError(f"Сделка {trade_id} не найдена")
            
            # Получаем текущую цену
            current_price = float(self.api_client.get_klines(
                symbol=trade.symbol,
                interval="1",
                limit=1
            )['result']['list'][0][4])
            
            # Рассчитываем PnL
            if trade.side == 'buy':
                pnl = (current_price - trade.price) * trade.amount
            else:
                pnl = (trade.price - current_price) * trade.amount
            
            # Обновляем PnL в БД
            trade.pnl = pnl
            self.session.commit()
            
            return pnl
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка расчета PnL: {e}")
            raise
    
    def close_position(self, trade_id: int) -> None:
        """Закрытие позиции"""
        try:
            trade = self.session.query(Trade).get(trade_id)
            if not trade:
                raise ValueError(f"Сделка {trade_id} не найдена")
            
            # Размещаем противоположный ордер
            opposite_side = 'sell' if trade.side == 'buy' else 'buy'
            self.api_client.place_order(
                symbol=trade.symbol,
                side=opposite_side,
                qty=trade.amount
            )
            
            # Обновляем статус сделки
            trade.status = 'closed'
            self.session.commit()
            
            logger.info(f"Позиция {trade_id} закрыта")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Ошибка закрытия позиции: {e}")
            raise 