# Руководство по деплою на сервер

## 🎯 Рекомендуемая последовательность

**Git → Сервер** (рекомендуется)

1. ✅ **Git обновлен** - все изменения сохранены
2. 🚀 **Деплой на сервер** - обновляем код на сервере

## 📋 Варианты деплоя

### Вариант 1: Автоматический деплой (PowerShell)

```powershell
# Запуск PowerShell скрипта
.\deploy_to_server.ps1
```

### Вариант 2: Ручной деплой

```bash
# Подключение к серверу
ssh root@5.35.82.47

# Переход в директорию проекта
cd /root/helperbt

# Остановка ботов
pkill -f "python.*bot.py"
pkill -f "python.*admin_bot.py" 
pkill -f "python.*auto_messenger.py"

# Обновление кода
git pull origin main

# Установка зависимостей
pip3 install -r requirements.txt

# Запуск ботов
nohup python3 start_bots_improved.py > logs/startup.log 2>&1 &
```

## 🔧 Проверка деплоя

### Проверка статуса ботов
```bash
ssh root@5.35.82.47 'ps aux | grep bot'
```

### Просмотр логов
```bash
# Основной бот
ssh root@5.35.82.47 'tail -f /root/helperbt/logs/main_bot.log'

# Админ-бот
ssh root@5.35.82.47 'tail -f /root/helperbt/logs/admin_bot.log'

# Автосообщения
ssh root@5.35.82.47 'tail -f /root/helperbt/logs/auto_messenger.log'
```

### Проверка работы ботов
- Основной бот: @bankruptcy_trading_bot
- Админ-бот: @bankruptcy_admin_bot (только для ID 1621867102)

## 🚨 Устранение неполадок

### Проблема: Боты не запускаются
```bash
# Проверяем логи запуска
ssh root@5.35.82.47 'cat /root/helperbt/logs/startup.log'

# Проверяем .env файл
ssh root@5.35.82.47 'ls -la /root/helperbt/.env'
```

### Проблема: Ошибки зависимостей
```bash
# Переустанавливаем зависимости
ssh root@5.35.82.47 'cd /root/helperbt && pip3 install -r requirements.txt --force-reinstall'
```

### Проблема: Порт занят
```bash
# Находим процесс, использующий порт
ssh root@5.35.82.47 'netstat -tulpn | grep :8000'

# Убиваем процесс
ssh root@5.35.82.47 'kill -9 <PID>'
```

## 📊 Мониторинг

### Автоматический перезапуск
Боты настроены на автоматический перезапуск при сбоях через `start_bots_improved.py`.

### Логи
- `logs/main_bot.log` - основной бот
- `logs/admin_bot.log` - админ-бот  
- `logs/auto_messenger.log` - автосообщения
- `logs/startup.log` - логи запуска

### Ротация логов
Логи автоматически ротируются при достижении 10MB.

## 🔄 Откат изменений

Если что-то пошло не так:

```bash
# Подключение к серверу
ssh root@5.35.82.47

# Переход в директорию
cd /root/helperbt

# Откат к предыдущему коммиту
git reset --hard HEAD~1

# Перезапуск ботов
pkill -f "python.*bot"
nohup python3 start_bots_improved.py > logs/startup.log 2>&1 &
```

## 📝 Чек-лист деплоя

- [ ] Код обновлен в Git
- [ ] SSH доступ к серверу настроен
- [ ] .env файл существует на сервере
- [ ] Зависимости установлены
- [ ] Боты запущены
- [ ] Логи проверены
- [ ] Функциональность протестирована

## 🆘 Экстренные команды

### Полная перезагрузка
```bash
ssh root@5.35.82.47 'cd /root/helperbt && pkill -f python && git pull && pip3 install -r requirements.txt && nohup python3 start_bots_improved.py > logs/startup.log 2>&1 &'
```

### Просмотр всех процессов
```bash
ssh root@5.35.82.47 'ps aux | grep -E "(bot|python)"'
```

### Очистка логов
```bash
ssh root@5.35.82.47 'cd /root/helperbt && find logs -name "*.log" -size +100M -delete'
```
