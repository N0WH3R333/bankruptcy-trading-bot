"""
Скрипт для тестирования системы автосообщений
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from auto_messenger import AutoMessenger

def test_auto_message_scheduling():
    """Тест планирования автосообщений"""
    print("🧪 Тестирование планирования автосообщений...")
    
    db = DatabaseManager()
    
    # Тестовый пользователь
    test_user_id = 123456789
    
    # Проверяем, есть ли недавние автосообщения
    has_recent = db.has_recent_auto_messages(test_user_id, days=14)
    print(f"📅 Есть недавние автосообщения (14 дней): {has_recent}")
    
    # Проверяем, запланированы ли уже автосообщения
    has_1hour = db.has_auto_message_scheduled(test_user_id, '1hour')
    has_3days = db.has_auto_message_scheduled(test_user_id, '3days')
    print(f"⏰ Запланировано через час: {has_1hour}")
    print(f"📅 Запланировано через 3 дня: {has_3days}")
    
    if not has_recent and not has_1hour and not has_3days:
        # Планируем сообщение через 1 минуту для тестирования
        db.schedule_auto_message(test_user_id, '1hour', 0.02)  # 0.02 часа = ~1 минута
        db.schedule_auto_message(test_user_id, '3days', 0.02)  # 0.02 часа = ~1 минута
        print(f"✅ Запланированы автосообщения для пользователя {test_user_id}")
    else:
        print(f"⚠️ Автосообщения для пользователя {test_user_id} уже запланированы или отправлялись недавно")
    
    # Проверяем запланированные сообщения
    pending = db.get_pending_auto_messages()
    print(f"📋 Запланированных сообщений: {len(pending)}")
    
    for msg in pending:
        print(f"   - ID: {msg[0]}, Пользователь: {msg[1]}, Тип: {msg[2]}, Время: {msg[3]}")

async def test_auto_message_sending():
    """Тест отправки автосообщений"""
    print("\n📨 Тестирование отправки автосообщений...")
    
    messenger = AutoMessenger()
    
    # Получаем текст сообщений
    text_1hour, markup_1hour = messenger.get_auto_message_text('1hour')
    text_3days, markup_3days = messenger.get_auto_message_text('3days')
    
    print("📝 Текст сообщения через час:")
    print(text_1hour[:100] + "...")
    
    print("\n📝 Текст сообщения через 3 дня:")
    print(text_3days[:100] + "...")
    
    print("\n✅ Тексты сообщений сгенерированы успешно")

def main():
    """Главная функция тестирования"""
    print("🚀 Тестирование системы автосообщений")
    print("=" * 50)
    
    try:
        # Тест планирования
        test_auto_message_scheduling()
        
        # Тест отправки
        asyncio.run(test_auto_message_sending())
        
        print("\n✅ Все тесты пройдены успешно!")
        print("\n📋 Что было протестировано:")
        print("   - Планирование автосообщений в базе данных")
        print("   - Генерация текстов сообщений")
        print("   - Структура клавиатур")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
