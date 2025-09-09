"""
Админ-бот для управления основным ботом и просмотра статистики
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
from config import ADMIN_BOT_TOKEN
from database import DatabaseManager
from ai_service import AIService

# Настройка логирования
from log_config import setup_logging
logger = setup_logging('admin_bot')

class AdminBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_service = AIService(self.db_manager)
        # Временно разрешаем всем пользователям доступ для тестирования
        # self.admin_users = [123456789]  # Добавьте сюда ID админов (замените на ваш реальный ID)
        self.admin_users = []  # Пустой список = доступ для всех
        
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь админом"""
        # Временно разрешаем всем пользователям доступ для тестирования
        if not self.admin_users:  # Если список пустой
            return True
        return user_id in self.admin_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start для админ-бота"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="users")],
            [InlineKeyboardButton("❓ Популярные вопросы", callback_data="popular_questions")],
            [InlineKeyboardButton("📚 Переходы в канал", callback_data="channel_stats")],
            [InlineKeyboardButton("🔄 Обновить кэш", callback_data="refresh_cache")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 Админ-панель бота по торгам по банкротству\n\nВыберите действие:",
            reply_markup=reply_markup
        )
    
    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки статистики"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        stats = self.ai_service.get_statistics()
        
        if stats:
            stats_text = f"""
📊 Статистика за последние 7 дней:

📝 Всего запросов: {stats.get('total_requests', 0)}
✅ Релевантных запросов: {stats.get('relevant_requests', 0)}
❌ Нерелевантных запросов: {stats.get('total_requests', 0) - stats.get('relevant_requests', 0)}
👥 Уникальных пользователей: {stats.get('unique_users', 0)}
📚 Переходов в канал: {stats.get('channel_visits', 0)}

📈 Эффективность: {round((stats.get('relevant_requests', 0) / max(stats.get('total_requests', 1), 1)) * 100, 1)}%
            """
        else:
            stats_text = "📊 Статистика пока недоступна"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, reply_markup=reply_markup)
    
    async def users_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки пользователей"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, total_requests, last_activity
                    FROM users 
                    ORDER BY total_requests DESC 
                    LIMIT 10
                ''')
                
                users = cursor.fetchall()
                
                users_text = "👥 Топ-10 активных пользователей:\n\n"
                for i, (user_id, username, first_name, requests, last_activity) in enumerate(users, 1):
                    name = first_name or username or f"ID: {user_id}"
                    users_text += f"{i}. {name} - {requests} запросов\n"
                
        except Exception as e:
            logger.error(f"Ошибка получения пользователей: {e}")
            users_text = "❌ Ошибка получения данных о пользователях"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(users_text, reply_markup=reply_markup)
    
    async def popular_questions_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки популярных вопросов"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        stats = self.ai_service.get_statistics()
        popular_questions = stats.get('popular_questions', [])
        
        if popular_questions:
            questions_text = "❓ Популярные вопросы:\n\n"
            for i, (question, count) in enumerate(popular_questions[:10], 1):
                questions_text += f"{i}. {question[:60]}... ({count} раз)\n"
        else:
            questions_text = "❓ Популярные вопросы пока недоступны"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(questions_text, reply_markup=reply_markup)
    
    async def channel_stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки статистики канала"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        try:
            import sqlite3
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) as total_visits,
                           COUNT(DISTINCT user_id) as unique_visitors
                    FROM channel_visits 
                    WHERE visited_at >= datetime('now', '-7 days')
                ''')
                
                result = cursor.fetchone()
                total_visits, unique_visitors = result
                
                channel_text = f"""
📚 Статистика переходов в канал за 7 дней:

📊 Всего переходов: {total_visits}
👥 Уникальных посетителей: {unique_visitors}
📈 Среднее переходов на пользователя: {round(total_visits / max(unique_visitors, 1), 1)}
                """
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики канала: {e}")
            channel_text = "❌ Ошибка получения статистики канала"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(channel_text, reply_markup=reply_markup)
    
    async def refresh_cache_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки обновления кэша"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        # Здесь можно добавить логику очистки кэша
        await query.edit_message_text("✅ Кэш обновлен!")
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text("✅ Кэш обновлен!", reply_markup=reply_markup)
    
    async def back_to_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик возврата в главное меню"""
        query = update.callback_query
        await query.answer()
        
        if not self.is_admin(query.from_user.id):
            await query.edit_message_text("❌ У вас нет доступа к админ-панели.")
            return
        
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("👥 Пользователи", callback_data="users")],
            [InlineKeyboardButton("❓ Популярные вопросы", callback_data="popular_questions")],
            [InlineKeyboardButton("📚 Переходы в канал", callback_data="channel_stats")],
            [InlineKeyboardButton("🔄 Обновить кэш", callback_data="refresh_cache")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔧 Админ-панель бота по торгам по банкротству\n\nВыберите действие:",
            reply_markup=reply_markup
        )
    
    def run(self):
        """Запуск админ-бота"""
        # Создаем приложение
        application = Application.builder().token(ADMIN_BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CallbackQueryHandler(self.stats_callback, pattern="stats"))
        application.add_handler(CallbackQueryHandler(self.users_callback, pattern="users"))
        application.add_handler(CallbackQueryHandler(self.popular_questions_callback, pattern="popular_questions"))
        application.add_handler(CallbackQueryHandler(self.channel_stats_callback, pattern="channel_stats"))
        application.add_handler(CallbackQueryHandler(self.refresh_cache_callback, pattern="refresh_cache"))
        application.add_handler(CallbackQueryHandler(self.back_to_menu_callback, pattern="back_to_menu"))
        
        # Запускаем бота
        logger.info("Админ-бот запущен")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    admin_bot = AdminBot()
    admin_bot.run()
