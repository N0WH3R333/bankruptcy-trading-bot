#!/usr/bin/env python3
"""
Тестовый файл для проверки админ-бота
"""

try:
    print("1. Импорт config...")
    from config import ADMIN_BOT_TOKEN
    print(f"   Токен загружен: {len(ADMIN_BOT_TOKEN)} символов")
    
    print("2. Импорт admin_bot...")
    from admin_bot import AdminBot
    print("   Импорт успешен")
    
    print("3. Создание экземпляра...")
    admin_bot = AdminBot()
    print("   Экземпляр создан")
    
    print("4. Проверка токена...")
    if ADMIN_BOT_TOKEN and ADMIN_BOT_TOKEN != 'YOUR_ADMIN_BOT_TOKEN_HERE':
        print("   Токен валидный")
    else:
        print("   Токен невалидный!")
        
    print("✅ Все проверки пройдены!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
