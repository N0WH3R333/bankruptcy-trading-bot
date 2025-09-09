"""
Скрипт для очистки старых логов
"""

import os
import sys
from log_config import cleanup_old_logs
from config import LOG_RETENTION_DAYS, LOG_DIR

def main():
    """Основная функция очистки логов"""
    print(f"🧹 Очистка логов старше {LOG_RETENTION_DAYS} дней...")
    
    try:
        cleanup_old_logs(LOG_DIR, LOG_RETENTION_DAYS)
        print("✅ Очистка логов завершена!")
    except Exception as e:
        print(f"❌ Ошибка при очистке логов: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
