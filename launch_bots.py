"""
Единый файл для запуска основного бота и админ-бота
"""

import asyncio
import logging
import threading
import time
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка логирования
from log_config import setup_logging
logger = setup_logging('launcher')

def run_main_bot():
    """Запуск основного бота"""
    try:
        logger.info("Запуск основного бота...")
        from bot import TradingBot
        bot = TradingBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска основного бота: {e}")
        print(f"Ошибка запуска основного бота: {e}")

def run_admin_bot():
    """Запуск админ-бота"""
    try:
        logger.info("Запуск админ-бота...")
        from admin_bot import AdminBot
        admin_bot = AdminBot()
        admin_bot.run()
    except Exception as e:
        logger.error(f"Ошибка запуска админ-бота: {e}")
        print(f"Ошибка запуска админ-бота: {e}")

def main():
    """Главная функция запуска"""
    print("🚀 Запуск ботов по торгам по банкротству...")
    print("📱 Основной бот: @bankruptcy_trading_bot")
    print("🔧 Админ-бот: @bankruptcy_admin_bot")
    print("=" * 50)
    
    # Запускаем основной бот в отдельном потоке
    main_bot_thread = threading.Thread(target=run_main_bot, daemon=True)
    main_bot_thread.start()
    
    # Небольшая задержка для запуска основного бота
    time.sleep(2)
    
    # Запускаем админ-бота в отдельном потоке
    admin_bot_thread = threading.Thread(target=run_admin_bot, daemon=True)
    admin_bot_thread.start()
    
    print("✅ Оба бота запущены!")
    print("📊 Логи записываются в директорию: logs/")
    print("   - Основной бот: logs/main_bot.log")
    print("   - Админ-бот: logs/admin_bot.log")
    print("   - Запуск: logs/launcher.log")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Держим главный поток активным
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Остановка ботов...")
        logger.info("Остановка ботов по команде пользователя")
        print("✅ Боты остановлены!")

if __name__ == "__main__":
    main()
