# Развертывание на сервере Beget

## Подготовка к развертыванию

### 1. Загрузка на GitHub

1. Создайте репозиторий на GitHub
2. Загрузите код:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/bankruptcy-trading-bot.git
git push -u origin main
```

### 2. Подготовка сервера

1. Подключитесь к серверу Beget по SSH
2. Клонируйте репозиторий:
```bash
cd /home/u1234567
git clone https://github.com/yourusername/bankruptcy-trading-bot.git bankruptcy_bot
cd bankruptcy_bot
```

### 3. Настройка окружения

1. Создайте файл `.env`:
```bash
cp env_example.txt .env
nano .env
```

2. Заполните токены в `.env`:
```env
TELEGRAM_BOT_TOKEN=your_main_bot_token
ADMIN_BOT_TOKEN=your_admin_bot_token
MISTRAL_API_KEY_1=your_mistral_api_key
KNOWLEDGE_CHANNEL_ID=your_channel_id
```

3. Настройте контакты в `config.py`:
```python
SPECIALIST_CONTACTS = {
    'phone': '+7 (495) 123-45-67',
    'telegram': '@your_username',
    'email': 'info@yourdomain.com',
    'website': 'https://yourdomain.com'
}
```

### 4. Автоматическое развертывание

Запустите скрипт развертывания:
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. Ручное развертывание

Если автоматический скрипт не работает:

1. Создайте директории:
```bash
mkdir -p /home/u1234567/bankruptcy_bot/{logs,data,backup}
```

2. Установите зависимости:
```bash
pip3 install --user -r requirements.txt
```

3. Настройте права:
```bash
chmod +x *.py
chmod 755 /home/u1234567/bankruptcy_bot
```

## Запуск бота

### Вариант 1: Ручной запуск
```bash
cd /home/u1234567/bankruptcy_bot
python3 launch_bots.py
```

### Вариант 2: Через systemd (рекомендуется)
```bash
# Копирование сервисного файла
sudo cp bankruptcy-trading-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bankruptcy-trading-bot
sudo systemctl start bankruptcy-trading-bot
```

### Вариант 3: Через screen/tmux
```bash
screen -S bankruptcy_bot
cd /home/u1234567/bankruptcy_bot
python3 launch_bots.py
# Нажмите Ctrl+A, затем D для отсоединения
```

## Управление ботом

### Проверка статуса
```bash
# Через systemd
sudo systemctl status bankruptcy-trading-bot

# Через процессы
ps aux | grep launch_bots.py
```

### Просмотр логов
```bash
# Логи systemd
sudo journalctl -u bankruptcy-trading-bot -f

# Логи файлов
tail -f /home/u1234567/bankruptcy_bot/logs/main_bot.log
tail -f /home/u1234567/bankruptcy_bot/logs/admin_bot.log
```

### Перезапуск
```bash
# Через systemd
sudo systemctl restart bankruptcy-trading-bot

# Ручной перезапуск
pkill -f launch_bots.py
cd /home/u1234567/bankruptcy_bot
python3 launch_bots.py &
```

## Изоляция от других ботов

### Уникальные имена
- База данных: `bankruptcy_trading_bot.db`
- Логи: в директории `logs/`
- PID файл: `bankruptcy_bot.pid`
- Сервис: `bankruptcy-trading-bot`

### Отдельные директории
- Проект: `/home/u1234567/bankruptcy_bot/`
- Логи: `/home/u1234567/bankruptcy_bot/logs/`
- Данные: `/home/u1234567/bankruptcy_bot/data/`

## Мониторинг

### Автоматический перезапуск
Systemd автоматически перезапускает бота при сбоях.

### Ротация логов
Логи автоматически ротируются при достижении 10MB.

### Очистка старых логов
```bash
cd /home/u1234567/bankruptcy_bot
python3 cleanup_logs.py
```

## Обновление

1. Остановите бота:
```bash
sudo systemctl stop bankruptcy-trading-bot
```

2. Обновите код:
```bash
cd /home/u1234567/bankruptcy_bot
git pull origin main
```

3. Установите новые зависимости:
```bash
pip3 install --user -r requirements.txt
```

4. Запустите бота:
```bash
sudo systemctl start bankruptcy-trading-bot
```

## Устранение неполадок

### Бот не запускается
1. Проверьте токены в `.env`
2. Проверьте права доступа к файлам
3. Проверьте логи: `sudo journalctl -u bankruptcy-trading-bot`

### Ошибки базы данных
1. Проверьте права на директорию `data/`
2. Убедитесь, что база данных не заблокирована

### Проблемы с логами
1. Проверьте права на директорию `logs/`
2. Убедитесь, что есть место на диске

## Безопасность

1. Не храните токены в коде
2. Используйте файл `.env` (добавлен в `.gitignore`)
3. Ограничьте права доступа к файлам
4. Регулярно обновляйте зависимости
