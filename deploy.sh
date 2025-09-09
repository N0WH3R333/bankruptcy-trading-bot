#!/bin/bash

# Скрипт для развертывания бота на сервере Beget

echo "🚀 Развертывание Bankruptcy Trading Bot на сервере..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что мы на сервере
if [[ ! -d "/home/u1234567" ]]; then
    log_error "Этот скрипт предназначен для запуска на сервере Beget"
    exit 1
fi

# Настройки проекта
PROJECT_NAME="bankruptcy_bot"
PROJECT_DIR="/home/u1234567/$PROJECT_NAME"
SERVICE_NAME="bankruptcy-trading-bot"

log_info "Настройка проекта: $PROJECT_NAME"
log_info "Директория проекта: $PROJECT_DIR"

# Создание директорий
log_info "Создание директорий..."
mkdir -p "$PROJECT_DIR"/{logs,data,backup}

# Копирование файлов (если они уже есть)
if [[ -f "launch_bots.py" ]]; then
    log_info "Копирование файлов проекта..."
    cp *.py "$PROJECT_DIR/"
    cp requirements.txt "$PROJECT_DIR/"
    cp *.md "$PROJECT_DIR/" 2>/dev/null || true
    cp *.service "$PROJECT_DIR/" 2>/dev/null || true
else
    log_warn "Файлы проекта не найдены. Убедитесь, что вы находитесь в директории с проектом."
fi

# Установка зависимостей
log_info "Установка зависимостей Python..."
cd "$PROJECT_DIR"
pip3 install --user -r requirements.txt

# Настройка прав доступа
log_info "Настройка прав доступа..."
chmod +x "$PROJECT_DIR"/*.py
chmod 755 "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR"/logs
chmod 755 "$PROJECT_DIR"/data

# Создание .env файла если его нет
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    log_warn "Файл .env не найден. Создайте его на основе env_example.txt"
    if [[ -f "$PROJECT_DIR/env_example.txt" ]]; then
        cp "$PROJECT_DIR/env_example.txt" "$PROJECT_DIR/.env"
        log_info "Создан файл .env из шаблона. Отредактируйте его с вашими токенами."
    fi
fi

# Настройка systemd сервиса (если доступен)
if command -v systemctl &> /dev/null; then
    log_info "Настройка systemd сервиса..."
    
    # Копирование сервисного файла
    if [[ -f "$PROJECT_DIR/bankruptcy-trading-bot.service" ]]; then
        sudo cp "$PROJECT_DIR/bankruptcy-trading-bot.service" /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        log_info "Сервис $SERVICE_NAME настроен и включен"
    else
        log_warn "Файл сервиса не найден. Настройте автозапуск вручную."
    fi
else
    log_warn "systemctl не доступен. Настройте автозапуск вручную."
fi

# Создание скрипта запуска
log_info "Создание скрипта запуска..."
cat > "$PROJECT_DIR/start_bot.sh" << 'EOF'
#!/bin/bash
cd /home/u1234567/bankruptcy_bot
python3 launch_bots.py
EOF

chmod +x "$PROJECT_DIR/start_bot.sh"

# Создание скрипта остановки
log_info "Создание скрипта остановки..."
cat > "$PROJECT_DIR/stop_bot.sh" << 'EOF'
#!/bin/bash
pkill -f "launch_bots.py"
pkill -f "bot.py"
pkill -f "admin_bot.py"
echo "Боты остановлены"
EOF

chmod +x "$PROJECT_DIR/stop_bot.sh"

# Создание скрипта перезапуска
log_info "Создание скрипта перезапуска..."
cat > "$PROJECT_DIR/restart_bot.sh" << 'EOF'
#!/bin/bash
cd /home/u1234567/bankruptcy_bot
./stop_bot.sh
sleep 2
./start_bot.sh
EOF

chmod +x "$PROJECT_DIR/restart_bot.sh"

log_info "✅ Развертывание завершено!"
log_info ""
log_info "Следующие шаги:"
log_info "1. Отредактируйте файл $PROJECT_DIR/.env с вашими токенами"
log_info "2. Настройте контакты в $PROJECT_DIR/config.py"
log_info "3. Запустите бота: cd $PROJECT_DIR && ./start_bot.sh"
log_info ""
log_info "Управление ботом:"
log_info "- Запуск: ./start_bot.sh"
log_info "- Остановка: ./stop_bot.sh"
log_info "- Перезапуск: ./restart_bot.sh"
log_info ""
if command -v systemctl &> /dev/null; then
    log_info "Управление через systemd:"
    log_info "- Запуск: sudo systemctl start $SERVICE_NAME"
    log_info "- Остановка: sudo systemctl stop $SERVICE_NAME"
    log_info "- Статус: sudo systemctl status $SERVICE_NAME"
    log_info "- Логи: sudo journalctl -u $SERVICE_NAME -f"
fi
