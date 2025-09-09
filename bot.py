"""
Основной файл Telegram бота по торгам по банкротству
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters, 
    ContextTypes
)
from config import TELEGRAM_BOT_TOKEN, KNOWLEDGE_CHANNEL_ID, SPECIALIST_CONTACTS, TRAINING_CONTACTS, MAX_MESSAGE_LENGTH
from database import DatabaseManager
from ai_service import AIService

# Настройка логирования
from log_config import setup_logging
logger = setup_logging('main_bot')

class TradingBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_service = AIService(self.db_manager)
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        self.db_manager.add_user(
            user.id, 
            user.username, 
            user.first_name, 
            user.last_name
        )
        
        keyboard = [
            [InlineKeyboardButton("🤖 Ответы на вопросы", callback_data="ask_question")],
            [InlineKeyboardButton("📚 База знаний", callback_data="knowledge_base")],
            [InlineKeyboardButton("👨‍💼 Связаться со специалистом", callback_data="contact_specialist")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🏛️ Добро пожаловать в бот по торгам по банкротству!

Я помогу вам разобраться в:
• Торгах по банкротству (ФЗ-127)
• Залоговом имуществе
• Документах для участия
• Стратегиях торгов
• Юридических аспектах

Выберите нужную функцию:
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 Справка по боту:

🤖 Ответы на вопросы - задайте вопрос по торгам по банкротству
📚 База знаний - перейти в канал с полезной информацией
👨‍💼 Связаться со специалистом - контакты наших экспертов

Команды:
/start - главное меню
/help - эта справка
/stats - статистика (только для админов)

Ограничения:
• Максимум 10 вопросов в минуту
• Ответы только по теме торгов по банкротству
        """
        await update.message.reply_text(help_text)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats (только для админов)"""
        user_id = update.effective_user.id
        
        # Здесь можно добавить проверку на админа
        # Пока что доступно всем для тестирования
        
        stats = self.ai_service.get_statistics()
        
        if stats:
            stats_text = f"""
📊 Статистика за последние 7 дней:

📝 Всего запросов: {stats.get('total_requests', 0)}
✅ Релевантных запросов: {stats.get('relevant_requests', 0)}
👥 Уникальных пользователей: {stats.get('unique_users', 0)}
📚 Переходов в канал: {stats.get('channel_visits', 0)}

🔥 Популярные вопросы:
            """
            
            for question, count in stats.get('popular_questions', [])[:5]:
                stats_text += f"\n• {question[:50]}... ({count} раз)"
        else:
            stats_text = "📊 Статистика пока недоступна"
        
        await update.message.reply_text(stats_text)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "ask_question":
            await query.edit_message_text(
                "🤖 Задайте ваш вопрос по торгам по банкротству:\n\n"
                "Я помогу с вопросами по:\n"
                "• Торгам по банкротству (ФЗ-127)\n"
                "• Залоговому имуществу\n"
                "• Документам для участия\n"
                "• Стратегиям торгов\n"
                "• Юридическим аспектам\n\n"
                "Просто напишите ваш вопрос в следующем сообщении."
            )
            
        elif query.data == "knowledge_base":
            # Логируем переход в канал
            self.db_manager.log_channel_visit(user_id)
            
            # Создаем кнопку для перехода в канал по ID
            keyboard = [
                [InlineKeyboardButton("📚 Перейти в канал", url=f"https://t.me/c/{KNOWLEDGE_CHANNEL_ID[4:]}")],
                [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📚 Наш канал с базой знаний:\n\n"
                f"Там вы найдете:\n"
                f"• Актуальную информацию о торгах\n"
                f"• Полезные статьи и гайды\n"
                f"• Новости законодательства\n"
                f"• Примеры успешных торгов\n\n"
                f"Нажмите кнопку ниже, чтобы перейти в канал:",
                reply_markup=reply_markup
            )
            
        elif query.data == "training":
            await query.edit_message_text(
                f"🎓 Обучение торгам по банкротству:\n\n"
                f"📞 Телефон: {TRAINING_CONTACTS['phone']}\n"
                f"💬 Telegram: {TRAINING_CONTACTS['telegram']}\n\n"
                f"Наши курсы включают:\n"
                f"• Основы торгов по банкротству\n"
                f"• Анализ лотов и рисков\n"
                f"• Стратегии участия\n"
                f"• Работа с документами\n"
                f"• Практические кейсы"
            )
            
        elif query.data == "contact_specialist":
            await query.edit_message_text(
                f"👨‍💼 Связаться со специалистом:\n\n"
                f"📞 Телефон: {SPECIALIST_CONTACTS['phone']}\n"
                f"💬 Telegram: {SPECIALIST_CONTACTS['telegram']}\n\n"
                f"Наши эксперты помогут:\n"
                f"• Выбрать подходящий лот\n"
                f"• Подготовить документы\n"
                f"• Разработать стратегию\n"
                f"• Решить юридические вопросы\n"
                f"• Сопроводить сделку"
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Проверяем лимиты пользователя
        if not self.db_manager.check_user_limits(user_id):
            await update.message.reply_text(
                "⏰ Слишком много запросов! Подождите минуту и попробуйте снова."
            )
            return
        
        # Увеличиваем счетчик запросов
        self.db_manager.increment_user_requests(user_id)
        
        # Планируем автосообщения только при первом вопросе пользователя
        self._schedule_follow_up_messages(user_id)
        
        # Проверяем длину сообщения
        if len(message_text) > MAX_MESSAGE_LENGTH:
            await update.message.reply_text(
                f"📝 Сообщение слишком длинное! Максимум {MAX_MESSAGE_LENGTH} символов."
            )
            return
        
        # Отправляем сообщение о том, что бот думает
        thinking_message = await update.message.reply_text("🤔 Думаю над ответом...")
        
        try:
            # Получаем ответ от ИИ
            result = self.ai_service.generate_answer(message_text, user_id)
            
            # Удаляем сообщение "думаю"
            await thinking_message.delete()
            
            # Отправляем ответ
            answer = result['answer']
            
            # Если ответ слишком длинный, разбиваем на части
            if len(answer) > MAX_MESSAGE_LENGTH:
                parts = [answer[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(answer), MAX_MESSAGE_LENGTH)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await update.message.reply_text(part)
                    else:
                        await update.message.reply_text(part)
            else:
                await update.message.reply_text(answer)
            
            # Показываем кнопки в зависимости от контекста
            keyboard = []
            
            # Если в ответе упоминаются специалисты, добавляем кнопку связи
            specialist_keywords = ['специалист', 'эксперт', 'консультац', 'помощь', 'анализ', 'наши специалисты', 'наши эксперты']
            if any(keyword in answer.lower() for keyword in specialist_keywords):
                keyboard.append([InlineKeyboardButton("👨‍💼 Связаться со специалистом", callback_data="contact_specialist")])
            
            # Всегда добавляем кнопку главного меню
            keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            await thinking_message.delete()
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик возврата в главное меню"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("🤖 Ответы на вопросы", callback_data="ask_question")],
            [InlineKeyboardButton("📚 База знаний", callback_data="knowledge_base")],
            [InlineKeyboardButton("👨‍💼 Связаться со специалистом", callback_data="contact_specialist")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🏛️ Главное меню бота по торгам по банкротству\n\nВыберите нужную функцию:",
            reply_markup=reply_markup
        )
    
    def _schedule_follow_up_messages(self, user_id: int):
        """Планирование автосообщений для пользователя"""
        try:
            # Исключаем админа из автосообщений
            if user_id == 1621867102:
                logger.info(f"Пользователь {user_id} - админ, автосообщения не планируются")
                return
            
            # Проверяем, не отправлялись ли уже автосообщения в последние 14 дней
            if self.db_manager.has_recent_auto_messages(user_id, days=14):
                logger.info(f"Пользователю {user_id} уже отправлялись автосообщения в последние 14 дней")
                return
            
            # Проверяем, не планировались ли уже автосообщения для этого пользователя
            if (self.db_manager.has_auto_message_scheduled(user_id, '1hour') or 
                self.db_manager.has_auto_message_scheduled(user_id, '3days')):
                logger.info(f"Автосообщения для пользователя {user_id} уже запланированы")
                return
            
            # Планируем сообщение через час
            self.db_manager.schedule_auto_message(user_id, '1hour', 1)
            logger.info(f"Запланировано автосообщение через час для пользователя {user_id}")
            
            # Планируем сообщение через 3 дня
            self.db_manager.schedule_auto_message(user_id, '3days', 72)  # 72 часа = 3 дня
            logger.info(f"Запланировано автосообщение через 3 дня для пользователя {user_id}")
                
        except Exception as e:
            logger.error(f"Ошибка планирования автосообщений: {e}")
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        # Сначала специфичные обработчики, потом общий
        application.add_handler(CallbackQueryHandler(self.main_menu_callback, pattern="main_menu"))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем бота
        logger.info("Бот запущен")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_async(self):
        """Асинхронный запуск бота"""
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        # Сначала специфичные обработчики, потом общий
        application.add_handler(CallbackQueryHandler(self.main_menu_callback, pattern="main_menu"))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем бота
        logger.info("Бот запущен")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
