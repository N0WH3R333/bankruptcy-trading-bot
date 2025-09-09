"""
Скрипт для очистки старых автосообщений из базы данных
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from log_config import setup_logging

logger = setup_logging('cleanup_auto_messages')

def cleanup_old_auto_messages(days_to_keep: int = 30):
    """Очистка старых автосообщений"""
    try:
        db = DatabaseManager()
        
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Удаляем старые отправленные автосообщения
            cursor.execute('''
                DELETE FROM auto_messages 
                WHERE sent = TRUE 
                AND sent_at < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            deleted_sent = cursor.rowcount
            
            # Удаляем старые неотправленные автосообщения (старше 7 дней)
            cursor.execute('''
                DELETE FROM auto_messages 
                WHERE sent = FALSE 
                AND created_at < datetime('now', '-7 days')
            ''')
            
            deleted_unsent = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Очистка завершена: удалено {deleted_sent} отправленных и {deleted_unsent} неотправленных автосообщений")
            print(f"✅ Очистка завершена:")
            print(f"   - Удалено отправленных автосообщений: {deleted_sent}")
            print(f"   - Удалено неотправленных автосообщений: {deleted_unsent}")
            
    except Exception as e:
        logger.error(f"Ошибка очистки автосообщений: {e}")
        print(f"❌ Ошибка очистки: {e}")

def show_auto_messages_stats():
    """Показать статистику автосообщений"""
    try:
        db = DatabaseManager()
        
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Общая статистика
            cursor.execute('SELECT COUNT(*) FROM auto_messages')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM auto_messages WHERE sent = TRUE')
            sent = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM auto_messages WHERE sent = FALSE')
            pending = cursor.fetchone()[0]
            
            # Статистика за последние 7 дней
            cursor.execute('''
                SELECT COUNT(*) FROM auto_messages 
                WHERE sent = TRUE AND sent_at >= datetime('now', '-7 days')
            ''')
            sent_week = cursor.fetchone()[0]
            
            print(f"📊 Статистика автосообщений:")
            print(f"   - Всего записей: {total}")
            print(f"   - Отправлено: {sent}")
            print(f"   - Ожидает отправки: {pending}")
            print(f"   - Отправлено за неделю: {sent_week}")
            
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        print(f"❌ Ошибка получения статистики: {e}")

def main():
    """Главная функция"""
    print("🧹 Очистка старых автосообщений")
    print("=" * 40)
    
    # Показываем текущую статистику
    show_auto_messages_stats()
    print()
    
    # Очищаем старые автосообщения
    cleanup_old_auto_messages(days_to_keep=30)
    
    print()
    print("📊 Статистика после очистки:")
    show_auto_messages_stats()

if __name__ == "__main__":
    main()
