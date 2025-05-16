# Торговый бот для Bybit

Торговый бот для автоматической торговли на бирже Bybit с использованием стратегии скользящей средней (SMA).

## Особенности

- Подключение к API Bybit (поддержка Testnet и Mainnet)
- Запись сделок в SQLite базу данных
- Расчет и отслеживание PnL
- Создание снимков баланса
- Модульная архитектура для легкого добавления новых стратегий
- Подробное логирование

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/trading_bot.git
cd trading_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте конфигурацию:
- Скопируйте `config/keys.json.example` в `config/keys.json`
- Добавьте ваши API ключи в `config/keys.json`
- Настройте параметры в `config/settings.json`

## Использование

1. Запустите бота:
```bash
python main.py
```

2. Бот будет:
- Подключаться к Bybit
- Инициализировать базу данных
- Начинать торговлю по стратегии SMA
- Логировать все действия

## Структура проекта

```
bybit_bot/
├── config/
│   ├── keys.json
│   └── settings.json
├── db/
│   ├── database.py
│   └── models.py
├── strategies/
│   ├── base_strategy.py
│   └── moving_average.py
├── core/
│   ├── api_client.py
│   ├── trade_manager.py
│   └── logger.py
└── main.py
```

## Добавление новых стратегий

1. Создайте новый файл в директории `strategies/`
2. Наследуйте класс от `BaseStrategy`
3. Реализуйте методы `update()` и `generate_signal()`
4. Добавьте новую стратегию в `main.py`

## Безопасность

- Храните API ключи в безопасном месте
- Используйте Testnet для тестирования
- Регулярно проверяйте логи на наличие ошибок

## Лицензия

MIT 