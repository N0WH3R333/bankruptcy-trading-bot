"""
Улучшенный запуск ботов с проверками и мониторингом
"""

import asyncio
import logging
import threading
import time
import sys
import os
import signal
import psutil
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_config import setup_logging
from config import LOG_DIR

# Настройка логирования
logger = setup_logging('bot_launcher')

class BotManager:
    def __init__(self):
        self.main_bot_process = None
        self.admin_bot_process = None
        self.auto_messenger_process = None
        self.running = False
        
    def check_dependencies(self):
        """Проверка зависимостей"""
        logger.info("Проверка зависимостей...")
        
        # Проверяем наличие .env файла
        if not os.path.exists('.env'):
            logger.error("Файл .env не найден! Создайте его на основе env_example.txt")
            return False
            
        # Проверяем наличие необходимых модулей
        try:
            import telegram
            import requests
            import dotenv
            logger.info("Все зависимости установлены")
            return True
        except ImportError as e:
            logger.error(f"Отсутствует зависимость: {e}")
            return False
    
    def create_directories(self):
        """Создание необходимых директорий"""
        directories = [LOG_DIR, 'data', 'backup']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"Директория {directory} готова")
    
    def run_main_bot(self):
        """Запуск основного бота"""
        try:
            logger.info("Запуск основного бота...")
            from bot import TradingBot
            bot = TradingBot()
            bot.run()
        except Exception as e:
            logger.error(f"Ошибка запуска основного бота: {e}")
            print(f"❌ Ошибка запуска основного бота: {e}")
    
    def run_admin_bot(self):
        """Запуск админ-бота"""
        try:
            logger.info("Запуск админ-бота...")
            from admin_bot import AdminBot
            admin_bot = AdminBot()
            admin_bot.run()
        except Exception as e:
            logger.error(f"Ошибка запуска админ-бота: {e}")
            print(f"❌ Ошибка запуска админ-бота: {e}")
    
    def run_auto_messenger(self):
        """Запуск планировщика автосообщений"""
        try:
            logger.info("Запуск планировщика автосообщений...")
            from auto_messenger import AutoMessenger
            messenger = AutoMessenger()
            asyncio.run(messenger.run_scheduler())
        except Exception as e:
            logger.error(f"Ошибка запуска планировщика автосообщений: {e}")
            print(f"❌ Ошибка запуска планировщика автосообщений: {e}")
    
    def monitor_bots(self):
        """Мониторинг состояния ботов"""
        while self.running:
            try:
                # Проверяем, что все потоки живы
                main_alive = self.main_bot_thread.is_alive() if hasattr(self, 'main_bot_thread') else False
                admin_alive = self.admin_bot_thread.is_alive() if hasattr(self, 'admin_bot_thread') else False
                messenger_alive = self.auto_messenger_thread.is_alive() if hasattr(self, 'auto_messenger_thread') else False
                
                if not main_alive:
                    logger.warning("Основной бот остановился, перезапускаем...")
                    self.main_bot_thread = threading.Thread(target=self.run_main_bot, daemon=True)
                    self.main_bot_thread.start()
                
                if not admin_alive:
                    logger.warning("Админ-бот остановился, перезапускаем...")
                    self.admin_bot_thread = threading.Thread(target=self.run_admin_bot, daemon=True)
                    self.admin_bot_thread.start()
                
                if not messenger_alive:
                    logger.warning("Планировщик автосообщений остановился, перезапускаем...")
                    self.auto_messenger_thread = threading.Thread(target=self.run_auto_messenger, daemon=True)
                    self.auto_messenger_thread.start()
                
                time.sleep(30)  # Проверяем каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка мониторинга: {e}")
                time.sleep(60)
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        self.running = False
        print("\n🛑 Получен сигнал завершения, останавливаем ботов...")
        sys.exit(0)
    
    def start(self):
        """Запуск ботов"""
        print("🚀 Запуск ботов по торгам по банкротству...")
        print("📱 Основной бот: @bankruptcy_trading_bot")
        print("🔧 Админ-бот: @bankruptcy_admin_bot")
        print("=" * 50)
        
        # Проверки
        if not self.check_dependencies():
            print("❌ Проверка зависимостей не пройдена!")
            return False
        
        self.create_directories()
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        
        # Запускаем основной бот
        self.main_bot_thread = threading.Thread(target=self.run_main_bot, daemon=True)
        self.main_bot_thread.start()
        
        # Небольшая задержка
        time.sleep(2)
        
        # Запускаем админ-бота
        self.admin_bot_thread = threading.Thread(target=self.run_admin_bot, daemon=True)
        self.admin_bot_thread.start()
        
        # Небольшая задержка
        time.sleep(2)
        
        # Запускаем планировщик автосообщений
        self.auto_messenger_thread = threading.Thread(target=self.run_auto_messenger, daemon=True)
        self.auto_messenger_thread.start()
        
        # Запускаем мониторинг
        monitor_thread = threading.Thread(target=self.monitor_bots, daemon=True)
        monitor_thread.start()
        
        print("✅ Все боты запущены!")
        print("📊 Логи записываются в директорию: logs/")
        print("   - Основной бот: logs/main_bot.log")
        print("   - Админ-бот: logs/admin_bot.log")
        print("   - Планировщик автосообщений: logs/auto_messenger.log")
        print("   - Запуск: logs/bot_launcher.log")
        print("🔄 Мониторинг активен (автоперезапуск при сбоях)")
        print("📨 Автосообщения: через 1 час и 3 дня после вопросов")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        try:
            # Держим главный поток активным
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n🛑 Остановка ботов...")
            logger.info("Остановка ботов по команде пользователя")
            print("✅ Боты остановлены!")
        
        return True

def main():
    """Главная функция"""
    manager = BotManager()
    success = manager.start()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
