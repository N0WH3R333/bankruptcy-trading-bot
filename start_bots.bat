@echo off
chcp 65001 >nul
echo 🚀 Запуск ботов по торгам по банкротству...
echo.

echo 🔄 Запуск основного бота...
start "Основной бот" cmd /k "C:\Users\Lenovo\AppData\Local\Microsoft\WindowsApps\python3.13.exe bot.py"

timeout /t 3 /nobreak >nul

echo 🔄 Запуск админ-бота...
start "Админ-бот" cmd /k "C:\Users\Lenovo\AppData\Local\Microsoft\WindowsApps\python3.13.exe admin_bot.py"

echo.
echo ✅ Оба бота запущены!
echo 📊 Логи:
echo    - Основной бот: bot.log
echo    - Админ-бот: admin_bot.log
echo.
echo ⏹️  Для остановки закройте окна ботов
echo ================================================
echo.
echo 💡 Теперь можете протестировать админ-бота!
echo    Отправьте /start в админ-бот
pause
