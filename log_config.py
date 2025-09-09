"""
Конфигурация логирования с ротацией файлов
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(log_name: str, log_file: str = None, max_bytes: int = 10*1024*1024, backup_count: int = 5):
    """
    Настройка логирования с ротацией файлов
    
    Args:
        log_name: Имя логгера
        log_file: Путь к файлу лога (если None, используется logs/{log_name}.log)
        max_bytes: Максимальный размер файла в байтах (по умолчанию 10MB)
        backup_count: Количество резервных файлов (по умолчанию 5)
    """
    
    # Создаем директорию для логов если её нет
    if log_file is None:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f"{log_name}.log")
    
    # Создаем логгер
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Создаем ротирующий файловый обработчик
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Создаем консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str):
    """Получить логгер по имени"""
    return logging.getLogger(name)

def cleanup_old_logs(log_dir: str = "logs", days_to_keep: int = 30):
    """
    Очистка старых логов
    
    Args:
        log_dir: Директория с логами
        days_to_keep: Количество дней для хранения логов
    """
    if not os.path.exists(log_dir):
        return
    
    import time
    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
    
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if file_time < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Удален старый лог: {filename}")
                except Exception as e:
                    print(f"Ошибка удаления {filename}: {e}")

# Настройки по умолчанию
DEFAULT_LOG_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5
DEFAULT_LOG_DIR = "logs"
