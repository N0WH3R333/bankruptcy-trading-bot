"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_requests INTEGER DEFAULT 0
                    )
                ''')
                
                # Таблица запросов и ответов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        question TEXT,
                        answer TEXT,
                        is_relevant BOOLEAN,
                        question_type TEXT,
                        response_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица переходов в канал
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS channel_visits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица кэша FAQ
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS faq_cache (
                        question_hash TEXT PRIMARY KEY,
                        question TEXT,
                        answer TEXT,
                        usage_count INTEGER DEFAULT 1,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE,
                        total_requests INTEGER DEFAULT 0,
                        relevant_requests INTEGER DEFAULT 0,
                        channel_visits INTEGER DEFAULT 0,
                        unique_users INTEGER DEFAULT 0
                    )
                ''')
                
                # Таблица ограничений пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_limits (
                        user_id INTEGER PRIMARY KEY,
                        requests_count INTEGER DEFAULT 0,
                        last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных инициализирована успешно")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
    
    def log_request(self, user_id: int, question: str, answer: str, is_relevant: bool, 
                   question_type: str = None, response_time: float = None):
        """Логирование запроса и ответа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO requests (user_id, question, answer, is_relevant, question_type, response_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, question, answer, is_relevant, question_type, response_time))
                
                # Обновляем счетчик запросов пользователя
                cursor.execute('''
                    UPDATE users SET total_requests = total_requests + 1, last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка логирования запроса: {e}")
    
    def log_channel_visit(self, user_id: int):
        """Логирование перехода в канал"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO channel_visits (user_id) VALUES (?)
                ''', (user_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка логирования перехода в канал: {e}")
    
    def check_user_limits(self, user_id: int) -> bool:
        """Проверка лимитов пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, нужно ли сбросить счетчик (прошла минута)
                cursor.execute('''
                    SELECT requests_count, last_reset FROM user_limits WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    requests_count, last_reset = result
                    last_reset = datetime.fromisoformat(last_reset)
                    
                    # Если прошла минута, сбрасываем счетчик
                    if datetime.now() - last_reset > timedelta(minutes=1):
                        cursor.execute('''
                            UPDATE user_limits SET requests_count = 0, last_reset = CURRENT_TIMESTAMP
                            WHERE user_id = ?
                        ''', (user_id,))
                        conn.commit()
                        return True
                    else:
                        return requests_count < 10  # MAX_REQUESTS_PER_MINUTE
                else:
                    # Создаем новую запись
                    cursor.execute('''
                        INSERT INTO user_limits (user_id, requests_count) VALUES (?, 0)
                    ''', (user_id,))
                    conn.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"Ошибка проверки лимитов пользователя: {e}")
            return True  # В случае ошибки разрешаем запрос
    
    def increment_user_requests(self, user_id: int):
        """Увеличение счетчика запросов пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_limits (user_id, requests_count, last_reset)
                    VALUES (?, COALESCE((SELECT requests_count FROM user_limits WHERE user_id = ?), 0) + 1, CURRENT_TIMESTAMP)
                ''', (user_id, user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка увеличения счетчика запросов: {e}")
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Получение статистики за указанное количество дней"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общая статистика
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(CASE WHEN is_relevant = 1 THEN 1 END) as relevant_requests,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM requests 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days))
                
                stats = cursor.fetchone()
                
                # Переходы в канал
                cursor.execute('''
                    SELECT COUNT(*) FROM channel_visits 
                    WHERE visited_at >= datetime('now', '-{} days')
                '''.format(days))
                
                channel_visits = cursor.fetchone()[0]
                
                # Популярные вопросы
                cursor.execute('''
                    SELECT question, COUNT(*) as count
                    FROM requests 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY question
                    ORDER BY count DESC
                    LIMIT 10
                '''.format(days))
                
                popular_questions = cursor.fetchall()
                
                return {
                    'total_requests': stats[0],
                    'relevant_requests': stats[1],
                    'unique_users': stats[2],
                    'channel_visits': channel_visits,
                    'popular_questions': popular_questions
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def cache_faq_answer(self, question_hash: str, question: str, answer: str):
        """Кэширование ответа FAQ"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO faq_cache (question_hash, question, answer, usage_count, last_used)
                    VALUES (?, ?, ?, COALESCE((SELECT usage_count FROM faq_cache WHERE question_hash = ?), 0) + 1, CURRENT_TIMESTAMP)
                ''', (question_hash, question, answer, question_hash))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка кэширования FAQ: {e}")
    
    def get_cached_faq(self, question_hash: str) -> Optional[str]:
        """Получение кэшированного ответа FAQ"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT answer FROM faq_cache WHERE question_hash = ?
                ''', (question_hash,))
                
                result = cursor.fetchone()
                if result:
                    # Обновляем время последнего использования
                    cursor.execute('''
                        UPDATE faq_cache SET last_used = CURRENT_TIMESTAMP WHERE question_hash = ?
                    ''', (question_hash,))
                    conn.commit()
                    return result[0]
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения кэшированного FAQ: {e}")
            return None
