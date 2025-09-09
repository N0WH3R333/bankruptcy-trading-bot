# PowerShell скрипт для деплоя бота на сервер
# Использование: .\deploy_to_server.ps1

Write-Host "🚀 Деплой бота по торгам по банкротству на сервер" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Настройки сервера
$SERVER_IP = "5.35.82.47"
$SERVER_USER = "root"
$PROJECT_DIR = "/root/helperbt"

Write-Host "📡 Подключение к серверу $SERVER_IP..." -ForegroundColor Yellow

# Проверяем SSH ключ
if (-not (Test-Path "$env:USERPROFILE\.ssh\id_rsa")) {
    Write-Host "🔑 SSH ключ не найден. Создайте его вручную или используйте пароль." -ForegroundColor Red
    Write-Host "Для создания SSH ключа выполните:" -ForegroundColor Yellow
    Write-Host "ssh-keygen -t rsa -b 4096 -f `$env:USERPROFILE\.ssh\id_rsa" -ForegroundColor Cyan
}

Write-Host "📥 Обновление кода на сервере..." -ForegroundColor Yellow

# Команды для выполнения на сервере
$serverCommands = @"
    # Переходим в директорию проекта
    cd /root/helperbt
    
    # Останавливаем ботов если они запущены
    echo "🛑 Остановка ботов..."
    pkill -f "python.*bot.py" || true
    pkill -f "python.*admin_bot.py" || true
    pkill -f "python.*auto_messenger.py" || true
    
    # Обновляем код из Git
    echo "📥 Обновление кода из Git..."
    git pull origin main
    
    # Устанавливаем зависимости
    echo "📦 Установка зависимостей..."
    pip3 install -r requirements.txt
    
    # Создаем директории для логов
    mkdir -p logs
    
    # Проверяем наличие .env файла
    if [ ! -f .env ]; then
        echo "⚠️  Файл .env не найден! Создайте его на основе env_example.txt"
        echo "📋 Необходимые переменные:"
        echo "   - TELEGRAM_BOT_TOKEN"
        echo "   - ADMIN_BOT_TOKEN"
        echo "   - MISTRAL_API_KEY_1, MISTRAL_API_KEY_2, MISTRAL_API_KEY_3"
        echo "   - KNOWLEDGE_CHANNEL_ID"
        exit 1
    fi
    
    # Запускаем ботов
    echo "🚀 Запуск ботов..."
    nohup python3 start_bots_improved.py > logs/startup.log 2>&1 &
    
    # Ждем немного и проверяем статус
    sleep 5
    
    echo "📊 Статус процессов:"
    ps aux | grep -E "(bot\.py|admin_bot\.py|auto_messenger\.py)" | grep -v grep
    
    echo "📋 Последние логи:"
    tail -20 logs/startup.log
    
    echo "✅ Деплой завершен!"
    echo "📊 Логи:"
    echo "   - Основной бот: logs/main_bot.log"
    echo "   - Админ-бот: logs/admin_bot.log"
    echo "   - Автосообщения: logs/auto_messenger.log"
    echo "   - Запуск: logs/startup.log"
"@

# Выполняем команды на сервере
try {
    $serverCommands | ssh "$SERVER_USER@$SERVER_IP" 'bash -s'
    Write-Host "✅ Деплой завершен успешно!" -ForegroundColor Green
} catch {
    Write-Host "❌ Ошибка при деплое: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Попробуйте подключиться вручную:" -ForegroundColor Yellow
    Write-Host "ssh $SERVER_USER@$SERVER_IP" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🎉 Деплой завершен!" -ForegroundColor Green
Write-Host "📱 Боты должны быть доступны:" -ForegroundColor Yellow
Write-Host "   - Основной бот: @bankruptcy_trading_bot" -ForegroundColor Cyan
Write-Host "   - Админ-бот: @bankruptcy_admin_bot" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Для проверки статуса выполните:" -ForegroundColor Yellow
Write-Host "   ssh $SERVER_USER@$SERVER_IP 'ps aux | grep bot'" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Для просмотра логов:" -ForegroundColor Yellow
Write-Host "   ssh $SERVER_USER@$SERVER_IP 'tail -f /root/helperbt/logs/main_bot.log'" -ForegroundColor Cyan
