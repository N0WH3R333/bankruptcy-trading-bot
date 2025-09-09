"""
Конфигурация для развертывания на сервере
"""

import os
from pathlib import Path

# Базовые настройки для сервера
SERVER_CONFIG = {
    # Уникальное имя проекта для избежания конфликтов
    'project_name': 'bankruptcy_trading_bot',
    
    # Директории
    'base_dir': '/home/u1234567/bankruptcy_bot',  # Замените на ваш путь
    'logs_dir': '/home/u1234567/bankruptcy_bot/logs',
    'data_dir': '/home/u1234567/bankruptcy_bot/data',
    
    # База данных с уникальным именем
    'database_path': '/home/u1234567/bankruptcy_bot/data/bankruptcy_trading_bot.db',
    
    # Настройки процесса
    'pid_file': '/home/u1234567/bankruptcy_bot/bankruptcy_bot.pid',
    'log_file': '/home/u1234567/bankruptcy_bot/logs/bankruptcy_bot.log',
    
    # Настройки для systemd (если используется)
    'service_name': 'bankruptcy-trading-bot',
    'user': 'u1234567',  # Замените на ваш пользователь
    'group': 'u1234567',  # Замените на вашу группу
}

def get_server_paths():
    """Получить пути для сервера"""
    return SERVER_CONFIG

def setup_server_directories():
    """Создать необходимые директории на сервере"""
    paths = get_server_paths()
    
    directories = [
        paths['base_dir'],
        paths['logs_dir'],
        paths['data_dir']
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Создана директория: {directory}")

def get_database_path():
    """Получить путь к базе данных для сервера"""
    return SERVER_CONFIG['database_path']

def get_log_path():
    """Получить путь к логам для сервера"""
    return SERVER_CONFIG['log_file']
