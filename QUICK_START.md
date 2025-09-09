# Быстрый старт

## 🚀 Запуск ботов

### Локальный запуск
```bash
# Простой запуск
python launch_bots.py

# Улучшенный запуск с мониторингом
python start_bots_improved.py
```

### Проверка статуса
```bash
python check_bots.py
```

## ⚙️ Настройка

### 1. Контакты
Отредактируйте `config.py`:
```python
SPECIALIST_CONTACTS = {
    'phone': '+7 (495) 123-45-67',
    'telegram': '@your_username',
    'email': 'info@yourdomain.com',
    'website': 'https://yourdomain.com'
}

TRAINING_CONTACTS = {
    'phone': '+7 (495) 765-43-21',
    'telegram': '@training_username',
    'email': 'training@yourdomain.com',
    'website': 'https://training.yourdomain.com'
}
```

### 2. Токены
Создайте файл `.env`:
```env
TELEGRAM_BOT_TOKEN=your_main_bot_token
ADMIN_BOT_TOKEN=your_admin_bot_token
MISTRAL_API_KEY_1=your_mistral_api_key
KNOWLEDGE_CHANNEL_ID=your_channel_id
```

## 📊 Логи

Логи сохраняются в директории `logs/`:
- `main_bot.log` - основной бот
- `admin_bot.log` - админ-бот
- `launcher.log` - запуск

Автоматическая ротация при достижении 10MB.

## 🗂️ Структура проекта

```
├── bot.py                    # Основной бот
├── admin_bot.py              # Админ-бот
├── launch_bots.py            # Простой запуск
├── start_bots_improved.py    # Улучшенный запуск
├── check_bots.py             # Проверка статуса
├── log_config.py             # Настройка логирования
├── config.py                 # Конфигурация
├── .env                      # Токены (создать)
├── logs/                     # Логи
├── data/                     # База данных
└── backup/                   # Резервные копии
```

## 🔧 Управление

### Запуск
```bash
python start_bots_improved.py
```

### Остановка
```bash
# Нажмите Ctrl+C в терминале
# Или найдите процесс и завершите его
pkill -f launch_bots.py
```

### Перезапуск
```bash
pkill -f launch_bots.py
python start_bots_improved.py
```

## 📱 Функции ботов

### Основной бот
- 🤖 Ответы на вопросы по торгам
- 📚 Переход в канал базы знаний
- 🎓 Контакты для обучения
- 👨‍💼 Связь со специалистами

### Админ-бот
- 📊 Статистика использования
- 👥 Информация о пользователях
- ❓ Популярные вопросы
- 📚 Статистика переходов в канал

## 🚀 Развертывание на сервере

1. Загрузите на GitHub
2. Клонируйте на сервер
3. Запустите `deploy.sh`
4. Настройте `.env` и контакты
5. Запустите ботов

Подробная инструкция в `DEPLOYMENT.md`

## ❓ Помощь

- Настройка контактов: `CONTACTS_SETUP.md`
- Развертывание: `DEPLOYMENT.md`
- Проверка статуса: `python check_bots.py`
