# Настройка контактов

## Где настроить контакты

Все контакты настраиваются в файле `config.py`:

### 1. Контакты специалистов (для консультаций)

```python
SPECIALIST_CONTACTS = {
    'phone': '+7 (XXX) XXX-XX-XX',  # Ваш телефон
    'telegram': '@your_username',   # Ваш Telegram
    'email': 'info@example.com',    # Ваш email
    'website': 'https://example.com' # Ваш сайт
}
```

### 2. Контакты для обучения

```python
TRAINING_CONTACTS = {
    'phone': '+7 (XXX) XXX-XX-XX',  # Телефон для обучения
    'telegram': '@training_username', # Telegram для обучения
    'email': 'training@example.com',  # Email для обучения
    'website': 'https://training.example.com' # Сайт с курсами
}
```

## Где используются контакты

### В основном боте:

1. **Кнопка "🎓 Обучение торгам"** - показывает `TRAINING_CONTACTS`
2. **Кнопка "👨‍💼 Связаться со специалистом"** - показывает `SPECIALIST_CONTACTS`
3. **Автоматически в ответах ИИ** - когда бот упоминает специалистов

### В админ-боте:

Контакты не используются напрямую, но доступны для расширения функционала.

## Пример настройки

```python
# Реальные контакты
SPECIALIST_CONTACTS = {
    'phone': '+7 (495) 123-45-67',
    'telegram': '@bankruptcy_expert',
    'email': 'consult@bankruptcy.ru',
    'website': 'https://bankruptcy-expert.ru'
}

TRAINING_CONTACTS = {
    'phone': '+7 (495) 765-43-21',
    'telegram': '@bankruptcy_training',
    'email': 'training@bankruptcy.ru',
    'website': 'https://bankruptcy-training.ru'
}
```

## Важные замечания

1. **Телефон** - используйте формат с кодом страны
2. **Telegram** - указывайте username с @ или полную ссылку
3. **Email** - проверьте, что email работает
4. **Сайт** - убедитесь, что ссылки ведут на рабочие страницы

После изменения контактов перезапустите ботов для применения изменений.
