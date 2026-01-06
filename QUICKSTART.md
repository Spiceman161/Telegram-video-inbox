# 🚀 Быстрый старт

## Автоматическая установка (рекомендуется)

```bash
# 1. Установите Termux из F-Droid
# 2. Откройте Termux и выполните:

termux-setup-storage  # Разрешить доступ к storage

cd ~
git clone https://github.com/yourusername/telegram-video-inbox.git
cd telegram-video-inbox

chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh

# 3. Настройте .env
nano .env
# Заполните: BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH, 
#            ALLOWED_USER_IDS, SHARED_DIR, TMP_DIR

# 4. Соберите Bot API Server (см. docs/INSTALLATION.md)

# 5. Запустите бота
./scripts/start_bot_api.sh &
./scripts/start_bot.sh &
```

## Ручная установка

```bash
# 1. Установите зависимости
pkg upgrade
pkg install python git ffmpeg

# 2. Клонируйте репозиторий
cd ~
git clone https://github.com/yourusername/telegram-video-inbox.git
cd telegram-video-inbox

# 3. Установите Python пакеты
pip install -r requirements.txt

# 4. Настройте конфигурацию
cp .env.example .env
nano .env

# 5. Создайте директории
mkdir -p logs tmp

# 6. Соберите Bot API Server (см. docs/INSTALLATION.md)

# 7. Запустите
./scripts/start_bot_api.sh &
./scripts/start_bot.sh &
```

## Проверка работы

```bash
# Проверить, что ffmpeg установлен
ffprobe -version

# Проверить, что бот запущен
ps aux | grep "python.*main.py"

# Посмотреть логи
tail -f logs/bot.log
```

## Автозапуск (Termux:Boot)

```bash
mkdir -p ~/.termux/boot
cp scripts/termux_boot_template.sh ~/.termux/boot/01-telegram-video-inbox.sh
chmod +x ~/.termux/boot/01-telegram-video-inbox.sh

# Откройте Termux:Boot хотя бы раз
# Перезагрузите устройство
```

## Полезные команды

```bash
# Перезапуск бота
pkill -f "python bot/main.py"
pkill telegram-bot-api
./scripts/start_bot_api.sh &
./scripts/start_bot.sh &

# Обновление
cd ~/telegram-video-inbox
git pull
./scripts/install_dependencies.sh

# Просмотр логов
tail -f logs/bot.log
tail -f logs/bot-api.log

# Тест метаданных видео
./scripts/test_aspect_ratio_fix.sh
```

## Troubleshooting

**Бот не отвечает:**
```bash
# 1. Проверить процессы
ps aux | grep telegram

# 2. Проверить логи
tail -f logs/bot.log

# 3. Перезапустить
pkill telegram-bot-api; pkill -f "python bot/main.py"
./scripts/start_bot_api.sh &
./scripts/start_bot.sh &
```

**ffmpeg не найден:**
```bash
pkg install ffmpeg
ffprobe -version  # Проверка
```

**Видео растянуто:**
```bash
# Проверить, что ffmpeg установлен
ffprobe -version

# Проверить, что используется SEND_AS=video
grep SEND_AS .env

# Перезапустить бота
pkill -f "python bot/main.py"
./scripts/start_bot.sh &
```

## Документация

- **README.md** - общий обзор
- **docs/INSTALLATION.md** - подробная установка
- **docs/AUTO_INSTALL.md** - автоматическая установка
- **docs/ASPECT_RATIO_FIX.md** - исправление соотношения сторон
- **docs/TESTING_ASPECT_RATIO.md** - тестирование

---

**Быстрая помощь:** Если что-то не работает, запустите:
```bash
./scripts/install_dependencies.sh
```
Скрипт переустановит все зависимости.
