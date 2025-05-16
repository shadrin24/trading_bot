from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    amount = Column(Float)
    price = Column(Float)
    fee = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    strategy = Column(String)
    pnl = Column(Float, default=0.0)
    status = Column(String, default="open")

class BalanceSnapshot(Base):
    __tablename__ = "balance_snapshots"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float)
    equity = Column(Float)
    margin = Column(Float)
    free_margin = Column(Float)

# Создание подключения к базе данных
engine = create_engine('sqlite:///trading_bot.db')
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine) 