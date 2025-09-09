"""
Исправленный запуск ботов с правильной обработкой asyncio
"""

import asyncio
import logging
import sys
import os
import signal
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_config import setup_logging

# Настройка логирования
logger = setup_logging('launcher')

async def run_main_bot():
    """Запуск основного бота"""
    try:
        logger.info("Запуск основного бота...")
        from bot import TradingBot
        bot = TradingBot()
        await bot.run_async()
    except Exception as e:
        logger.error(f"Ошибка запуска основного бота: {e}")
        print(f"Ошибка запуска основного бота: {e}")

async def run_admin_bot():
    """Запуск админ-бота"""
    try:
        logger.info("Запуск админ-бота...")
        from admin_bot import AdminBot
        admin_bot = AdminBot()
        await admin_bot.run_async()
    except Exception as e:
        logger.error(f"Ошибка запуска админ-бота: {e}")
        print(f"Ошибка запуска админ-бота: {e}")

async def main():
    """Главная функция запуска"""
    print("🚀 Запуск ботов по торгам по банкротству...")
    print("📱 Основной бот: @bankruptcy_trading_bot")
    print("🔧 Админ-бот: @bankruptcy_admin_bot")
    print("=" * 50)
    
    # Создаем задачи для обоих ботов
    main_task = asyncio.create_task(run_main_bot())
    admin_task = asyncio.create_task(run_admin_bot())
    
    print("✅ Оба бота запущены!")
    print("📊 Логи записываются в директорию: logs/")
    print("   - Основной бот: logs/main_bot.log")
    print("   - Админ-бот: logs/admin_bot.log")
    print("   - Запуск: logs/launcher.log")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    try:
        # Ждем завершения обеих задач
        await asyncio.gather(main_task, admin_task)
    except KeyboardInterrupt:
        print("\n🛑 Остановка ботов...")
        logger.info("Остановка ботов по команде пользователя")
        
        # Отменяем задачи
        main_task.cancel()
        admin_task.cancel()
        
        # Ждем завершения отмены
        try:
            await asyncio.gather(main_task, admin_task, return_exceptions=True)
        except Exception:
            pass
        
        print("✅ Боты остановлены!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановка...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
