"""
Конфигурационный файл для Telegram бота по торгам по банкротству
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN', 'YOUR_ADMIN_BOT_TOKEN_HERE')

# Mistral API настройки
MISTRAL_API_KEYS = [
    os.getenv('MISTRAL_API_KEY_1', 'YOUR_MISTRAL_API_KEY_1_HERE'),
    os.getenv('MISTRAL_API_KEY_2', 'YOUR_MISTRAL_API_KEY_2_HERE'),
    os.getenv('MISTRAL_API_KEY_3', 'YOUR_MISTRAL_API_KEY_3_HERE'),
]
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# Канал базы знаний
KNOWLEDGE_CHANNEL_ID = os.getenv('KNOWLEDGE_CHANNEL_ID', 'YOUR_CHANNEL_ID_HERE')

# Контакты специалистов
SPECIALIST_CONTACTS = {
    'phone': '+79054652977',  # Замените на реальные контакты
    'telegram': '@N0WH3R33',  # Замените на реальные контакты
}

# Контакты для обучения
TRAINING_CONTACTS = {
    'phone': '+79911112025',  # Замените на реальные контакты
    'telegram': '@N0WH3R33',  # Замените на реальные контакты
}

# Настройки безопасности
MAX_REQUESTS_PER_MINUTE = 10  # Максимум запросов в минуту от одного пользователя
MAX_MESSAGE_LENGTH = 4000  # Максимальная длина сообщения

# Настройки базы данных
DATABASE_PATH = 'trading_bot.db'

# Настройки логирования
LOG_DIR = 'logs'
LOG_LEVEL = 'INFO'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
LOG_RETENTION_DAYS = 30

# Настройки кэширования
CACHE_SIZE = 100  # Количество кэшированных ответов
CACHE_TTL = 3600  # Время жизни кэша в секундах (1 час)
