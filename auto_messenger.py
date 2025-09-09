"""
Модуль для отправки автосообщений пользователям
"""

import asyncio
import logging
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, SPECIALIST_CONTACTS
from database import DatabaseManager
from log_config import setup_logging

logger = setup_logging('auto_messenger')

class AutoMessenger:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.db_manager = DatabaseManager()
        
    def get_auto_message_text(self, message_type: str) -> tuple:
        """Получение текста автосообщения по типу"""
        if message_type == '1hour':
            text = """🤔 Остались ли у вас вопросы по торгам по банкротству?

Если у вас есть дополнительные вопросы, я готов помочь! 

Вы можете:
• Задать новый вопрос
• Получить консультацию специалиста
• Изучить базу знаний"""
            
            keyboard = [
                [InlineKeyboardButton("🤖 Задать вопрос", callback_data="ask_question")],
                [InlineKeyboardButton("👨‍💼 Связаться со специалистом", callback_data="contact_specialist")],
                [InlineKeyboardButton("📚 База знаний", callback_data="knowledge_base")]
            ]
            
        elif message_type == '3days':
            text = f"""🏛️ Мы видим, что у вас есть вопросы о торгах по банкротству

Наши специалисты готовы помочь вам отыграть любой лот для любых целей!

📞 Телефон: {SPECIALIST_CONTACTS['phone']}
💬 Telegram: {SPECIALIST_CONTACTS['telegram']}

Наши эксперты помогут:
• Выбрать подходящий лот
• Подготовить документы
• Разработать стратегию торгов
• Решить юридические вопросы
• Сопроводить сделку
• Убедиться в юридической чистоте имущества
• Заранее узнать техническое состояние имущества и согласовать осмотр
Не упустите возможность получить профессиональную помощь!"""
            
            keyboard = [
                [InlineKeyboardButton("👨‍💼 Связаться со специалистом", callback_data="contact_specialist")],
                [InlineKeyboardButton("🤖 Задать вопрос", callback_data="ask_question")],
                [InlineKeyboardButton("📚 База знаний", callback_data="knowledge_base")]
            ]
        
        else:
            return None, None
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        return text, reply_markup
    
    async def send_auto_message(self, user_id: int, message_type: str) -> bool:
        """Отправка автосообщения пользователю"""
        try:
            text, reply_markup = self.get_auto_message_text(message_type)
            if not text:
                logger.error(f"Неизвестный тип сообщения: {message_type}")
                return False
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup
            )
            
            logger.info(f"Автосообщение {message_type} отправлено пользователю {user_id}")
            return True
            
        except TelegramError as e:
            if "Forbidden" in str(e) or "bot was blocked" in str(e).lower():
                logger.warning(f"Пользователь {user_id} заблокировал бота")
            else:
                logger.error(f"Ошибка отправки автосообщения пользователю {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке автосообщения: {e}")
            return False
    
    async def process_pending_messages(self):
        """Обработка запланированных автосообщений"""
        try:
            pending_messages = self.db_manager.get_pending_auto_messages()
            
            for message_id, user_id, message_type, scheduled_time in pending_messages:
                logger.info(f"Обработка автосообщения {message_id} для пользователя {user_id}")
                
                success = await self.send_auto_message(user_id, message_type)
                
                # Отмечаем сообщение как отправленное независимо от результата
                self.db_manager.mark_auto_message_sent(message_id)
                
                if success:
                    logger.info(f"Автосообщение {message_id} успешно отправлено")
                else:
                    logger.warning(f"Не удалось отправить автосообщение {message_id}")
                
                # Небольшая пауза между отправками
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Ошибка обработки запланированных сообщений: {e}")
    
    async def run_scheduler(self):
        """Запуск планировщика автосообщений"""
        logger.info("Планировщик автосообщений запущен")
        
        while True:
            try:
                await self.process_pending_messages()
                # Проверяем каждые 5 минут
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Ошибка в планировщике автосообщений: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке

if __name__ == "__main__":
    # Запуск планировщика
    messenger = AutoMessenger()
    asyncio.run(messenger.run_scheduler())
