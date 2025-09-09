"""
Скрипт для проверки статуса ботов
"""

import os
import sys
import psutil
from pathlib import Path

def check_bot_status():
    """Проверка статуса ботов"""
    print("🔍 Проверка статуса ботов...")
    print("=" * 50)
    
    # Проверяем процессы
    bot_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'launch_bots.py' in cmdline or 'start_bots_improved.py' in cmdline:
                bot_processes.append(proc.info)
            elif 'bot.py' in cmdline and 'admin_bot.py' not in cmdline:
                bot_processes.append(proc.info)
            elif 'admin_bot.py' in cmdline:
                bot_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if bot_processes:
        print("✅ Найдены запущенные процессы ботов:")
        for proc in bot_processes:
            print(f"   PID: {proc['pid']}, Команда: {' '.join(proc['cmdline'][:3])}...")
    else:
        print("❌ Боты не запущены")
    
    # Проверяем логи
    print("\n📊 Проверка логов:")
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"   {log_file.name}: {size} байт")
        else:
            print("   Логи не найдены")
    else:
        print("   Директория логов не найдена")
    
    # Проверяем базу данных
    print("\n💾 Проверка базы данных:")
    db_files = list(Path(".").glob("*.db"))
    if db_files:
        for db_file in db_files:
            size = db_file.stat().st_size
            print(f"   {db_file.name}: {size} байт")
    else:
        print("   База данных не найдена")
    
    # Проверяем конфигурацию
    print("\n⚙️  Проверка конфигурации:")
    config_files = ['.env', 'config.py']
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file} найден")
        else:
            print(f"   ❌ {config_file} не найден")
    
    print("\n" + "=" * 50)

def main():
    """Главная функция"""
    try:
        check_bot_status()
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
