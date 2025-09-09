"""
Сервис для работы с Mistral API
"""

import requests
import json
import hashlib
import logging
import time
import random
from typing import Optional, Dict, Any
from config import MISTRAL_API_KEYS, MISTRAL_API_URL
from prompts import (
    MAIN_SYSTEM_PROMPT, 
    RELEVANCE_CHECK_PROMPT, 
    QUESTION_TYPE_PROMPTS,
    FAQ_CACHE,
    ERROR_PROMPT
)
from database import DatabaseManager

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, db_manager: DatabaseManager):
        # Фильтруем только валидные API ключи
        self.api_keys = [key for key in MISTRAL_API_KEYS if key and key not in ['YOUR_MISTRAL_API_KEY_1_HERE', 'YOUR_MISTRAL_API_KEY_2_HERE', 'YOUR_MISTRAL_API_KEY_3_HERE', '']]
        self.api_url = MISTRAL_API_URL
        self.db_manager = db_manager
        self.current_key_index = 0
        
        # Если нет API ключей, используем режим FAQ
        if not self.api_keys:
            logger.warning("API ключи Mistral не настроены, используется только FAQ кэш")
        
    def _get_next_api_key(self) -> Optional[str]:
        """Получение следующего доступного API ключа"""
        if not self.api_keys:
            return None
        
        # Ротация ключей для равномерной нагрузки
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    def _make_request(self, messages: list, max_tokens: int = 1000) -> Optional[str]:
        """Отправка запроса к Mistral API с ротацией ключей"""
        if not self.api_keys:
            logger.error("Нет доступных API ключей Mistral")
            return None
            
        # Пробуем все ключи по очереди
        for attempt in range(len(self.api_keys)):
            api_key = self._get_next_api_key()
            
            try:
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'mistral-small-latest',
                    'messages': messages,
                    'max_tokens': max_tokens,
                    'temperature': 0.7
                }
                
                response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                elif response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limit для ключа {api_key[:10]}...")
                    continue  # Пробуем следующий ключ
                else:
                    logger.error(f"Ошибка API Mistral: {response.status_code} - {response.text}")
                    continue
                    
            except Exception as e:
                logger.error(f"Ошибка запроса к Mistral API с ключом {api_key[:10]}...: {e}")
                continue
        
        logger.error("Все API ключи недоступны")
        return None
    
    def _check_relevance(self, question: str) -> bool:
        """Проверка релевантности вопроса - более гибкая логика"""
        try:
            question_lower = question.lower().strip()
            
            # Вежливые фразы всегда релевантны
            polite_phrases = ['спасибо', 'благодарю', 'привет', 'здравствуйте', 'до свидания', 'пока']
            if any(phrase in question_lower for phrase in polite_phrases):
                return True
            
            # Расширенный список ключевых слов для торгов по банкротству
            trade_keywords = [
                # Основные термины
                'торг', 'банкрот', 'несостоятельность', 'конкурс',
                # Имущество и недвижимость
                'залог', 'имуществ', 'недвижим', 'квартир', 'дом', 'участок', 'земл',
                # Процедуры и документы
                'документ', 'участие', 'лот', 'ставка', 'аукцион', 'продаж',
                # Финансы
                'долг', 'кредит', 'обязательств', 'требовани', 'денег', 'стоимость',
                # Юридические аспекты
                'суд', 'закон', 'право', 'статья', 'фз', 'кодекс',
                # Участники
                'управляющ', 'кредитор', 'должник', 'участник',
                # Общие экономические термины
                'собственность', 'приобретение', 'покупка', 'инвестиц',
                # Документы и процедуры
                'акт', 'хранен', 'ответственн', 'передач', 'приемк'
            ]
            
            # Проверяем наличие ключевых слов
            has_trade_keywords = any(keyword in question_lower for keyword in trade_keywords)
            
            # Если есть ключевые слова - считаем релевантным
            if has_trade_keywords:
                return True
            
            # Если нет ключевых слов, но есть API ключи - используем ИИ для проверки
            if self.api_keys:
                messages = [
                    {"role": "user", "content": RELEVANCE_CHECK_PROMPT.format(question=question)}
                ]
                
                response = self._make_request(messages, max_tokens=10)
                return response and response.strip().upper() == "ДА"
            
            # Если нет API ключей и нет ключевых слов - считаем нерелевантным
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки релевантности: {e}")
            return True  # В случае ошибки считаем релевантным
    
    def _get_question_type(self, question: str) -> str:
        """Определение типа вопроса"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['документ', 'справка', 'пакет', 'заявка']):
            return 'documents'
        elif any(word in question_lower for word in ['стратегия', 'выбор', 'лота', 'ставка']):
            return 'strategy'
        elif any(word in question_lower for word in ['закон', 'статья', 'фз', 'право', 'суд']):
            return 'legal'
        elif any(word in question_lower for word in ['недвижимость', 'имущество', 'квартира', 'дом']):
            return 'property'
        else:
            return 'general'
    
    def _check_faq_cache(self, question: str) -> Optional[str]:
        """Проверка кэша FAQ"""
        try:
            # Создаем хэш вопроса для поиска в кэше
            question_hash = hashlib.md5(question.lower().strip().encode()).hexdigest()
            
            # Проверяем в базе данных
            cached_answer = self.db_manager.get_cached_faq(question_hash)
            if cached_answer:
                return cached_answer
            
            # Проверяем в локальном кэше
            question_lower = question.lower().strip()
            
            # Сначала ищем точное совпадение
            for faq_question, faq_answer in FAQ_CACHE.items():
                if faq_question in question_lower:
                    # Кэшируем в базе данных
                    self.db_manager.cache_faq_answer(question_hash, question, faq_answer)
                    return faq_answer
            
            # Затем ищем по ключевым словам
            for faq_question, faq_answer in FAQ_CACHE.items():
                faq_words = faq_question.split()
                if len(faq_words) >= 2:  # Только для вопросов из 2+ слов
                    if any(word in question_lower for word in faq_words):
                        # Кэшируем в базе данных
                        self.db_manager.cache_faq_answer(question_hash, question, faq_answer)
                        return faq_answer
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка проверки кэша FAQ: {e}")
            return None
    
    def generate_answer(self, question: str, user_id: int) -> Dict[str, Any]:
        """Генерация ответа на вопрос"""
        start_time = time.time()
        
        try:
            # Сначала проверяем простые вежливые фразы в кэше
            question_lower = question.lower().strip()
            polite_phrases = ['спасибо', 'благодарю', 'привет', 'здравствуйте', 'до свидания', 'пока']
            
            if any(phrase in question_lower for phrase in polite_phrases):
                cached_answer = self._check_faq_cache(question)
                if cached_answer:
                    response_time = time.time() - start_time
                    self.db_manager.log_request(user_id, question, cached_answer, True, 'cached', response_time)
                    return {
                        'answer': cached_answer,
                        'is_relevant': True,
                        'question_type': 'cached',
                        'response_time': response_time
                    }
            
            # Проверяем релевантность
            is_relevant = self._check_relevance(question)
            
            if not is_relevant:
                irrelevant_answer = "Извините, я специализируюсь только на вопросах, связанных с торгами по банкротству. Задайте, пожалуйста, вопрос по этой теме."
                response_time = time.time() - start_time
                self.db_manager.log_request(user_id, question, irrelevant_answer, False, 'irrelevant', response_time)
                return {
                    'answer': irrelevant_answer,
                    'is_relevant': False,
                    'question_type': 'irrelevant',
                    'response_time': response_time
                }
            
            # Если есть API ключи, используем ИИ
            if self.api_keys:
                # Определяем тип вопроса
                question_type = self._get_question_type(question)
                
                # Формируем промпт
                system_prompt = MAIN_SYSTEM_PROMPT
                if question_type in QUESTION_TYPE_PROMPTS:
                    system_prompt += "\n\n" + QUESTION_TYPE_PROMPTS[question_type]
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ]
                
                # Отправляем запрос к API
                answer = self._make_request(messages)
                
                if answer:
                    response_time = time.time() - start_time
                    self.db_manager.log_request(user_id, question, answer, True, question_type, response_time)
                    return {
                        'answer': answer,
                        'is_relevant': True,
                        'question_type': question_type,
                        'response_time': response_time
                    }
            
            # Fallback: проверяем кэш FAQ для сложных вопросов
            cached_answer = self._check_faq_cache(question)
            if cached_answer:
                response_time = time.time() - start_time
                self.db_manager.log_request(user_id, question, cached_answer, True, 'cached', response_time)
                return {
                    'answer': cached_answer,
                    'is_relevant': True,
                    'question_type': 'cached',
                    'response_time': response_time
                }
            
            # Если ничего не найдено, возвращаем общий ответ
            fallback_answer = "Я готов помочь вам с вопросами по торгам по банкротству. Можете задать более конкретный вопрос?"
            response_time = time.time() - start_time
            self.db_manager.log_request(user_id, question, fallback_answer, True, 'fallback', response_time)
            
            return {
                'answer': fallback_answer,
                'is_relevant': True,
                'question_type': 'fallback',
                'response_time': response_time
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            response_time = time.time() - start_time
            error_answer = ERROR_PROMPT
            self.db_manager.log_request(user_id, question, error_answer, False, 'error', response_time)
            
            return {
                'answer': error_answer,
                'is_relevant': False,
                'question_type': 'error',
                'response_time': response_time
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики использования ИИ"""
        try:
            return self.db_manager.get_statistics()
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
