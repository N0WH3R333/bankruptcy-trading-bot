"""
Простой запуск обоих ботов через subprocess
"""

import subprocess
import sys
import time
import os

def main():
    print("🚀 Запуск ботов по торгам по банкротству...")
    print("📱 Основной бот и админ-бот запускаются...")
    print("=" * 50)
    
    try:
        # Запускаем основной бот
        print("🔄 Запуск основного бота...")
        main_bot_process = subprocess.Popen([sys.executable, "bot.py"])
        
        # Небольшая задержка
        time.sleep(2)
        
        # Запускаем админ-бота
        print("🔄 Запуск админ-бота...")
        admin_bot_process = subprocess.Popen([sys.executable, "admin_bot.py"])
        
        print("✅ Оба бота запущены!")
        print("📊 Логи:")
        print("   - Основной бот: bot.log")
        print("   - Админ-бот: admin_bot.log")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        # Ждем завершения процессов
        try:
            main_bot_process.wait()
            admin_bot_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Остановка ботов...")
            main_bot_process.terminate()
            admin_bot_process.terminate()
            print("✅ Боты остановлены!")
            
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main()
