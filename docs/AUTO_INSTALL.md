# Автоматическая установка зависимостей

## Описание

Скрипт `install_dependencies.sh` автоматически устанавливает все зависимости, необходимые для работы Telegram Video Inbox Bot, включая:

- **Системные пакеты**: Python, Git, **ffmpeg**
- **Python пакеты**: python-telegram-bot, python-dotenv
- **Директории**: `logs/`, `tmp/`
- **Конфигурация**: создает `.env` из `.env.example` (если не существует)

## Поддерживаемые платформы

- ✅ **Termux** (Android) - основная целевая платформа
- ✅ **Debian/Ubuntu** - полная поддержка
- ✅ **RHEL/CentOS** - базовая поддержка
- ⚠️ **Другие Linux дистрибутивы** - может потребоваться ручная установка

## Использование

### Базовое использование

```bash
cd ~/telegram-video-inbox
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

### Что делает скрипт

1. **Определяет окружение** (Termux/Debian/RHEL)
2. **Устанавливает системные пакеты**:
   - Termux: `pkg install -y python git ffmpeg`
   - Debian/Ubuntu: `apt install -y python3 python3-pip git ffmpeg`
3. **Обновляет pip**: `python -m pip install --upgrade pip`
4. **Устанавливает Python зависимости**: `pip install -r requirements.txt`
5. **Создает директории**: `logs/`, `tmp/`
6. **Проверяет .env**: создает из `.env.example`, если не существует
7. **Верифицирует установку**: проверяет наличие ffprobe

### Пример вывода

```
╔════════════════════════════════════════════════════════════╗
║   Telegram Video Inbox Bot - Dependency Installer         ║
╚════════════════════════════════════════════════════════════╝

✓ Detected environment: Termux

════════════════════════════════════════════════════════════
  Step 1: Installing system packages
════════════════════════════════════════════════════════════

📦 Installing: Python, Git, ffmpeg
→ Running: pkg install -y python git ffmpeg
[...]
✓ System packages installed successfully

✓ ffprobe installed: ffprobe version 4.4.2

════════════════════════════════════════════════════════════
  Step 2: Installing Python dependencies
════════════════════════════════════════════════════════════

→ Upgrading pip...
→ Installing Python packages from requirements.txt...
[...]
✓ Python dependencies installed successfully

════════════════════════════════════════════════════════════
  Step 3: Creating required directories
════════════════════════════════════════════════════════════

✓ Created: logs/
✓ Created: tmp/

⚠️  Notice: .env file not found
   Creating .env from .env.example...
✓ Created .env file

   ⚠️  IMPORTANT: Edit .env file and fill in your credentials!

════════════════════════════════════════════════════════════
  Installation Summary
════════════════════════════════════════════════════════════

✅ System packages: Installed
✅ Python packages: Installed
✅ Directories: Created
✅ ffmpeg: Verified

Verification:
  • Python: Python 3.11.4
  • pip: pip 23.2.1
  • ffprobe: ffprobe version 4.4.2

════════════════════════════════════════════════════════════
  Next Steps
════════════════════════════════════════════════════════════

1. Configure the bot:
   nano .env
   (Fill in BOT_TOKEN, API credentials, user IDs, paths)

2. Build Telegram Bot API server (see docs/INSTALLATION.md)

3. Start the bot:
   ./scripts/start_bot_api.sh &
   ./scripts/start_bot.sh &

╔════════════════════════════════════════════════════════════╗
║   Installation completed successfully! 🎉                  ║
╚════════════════════════════════════════════════════════════╝
```

## Особенности

### Автоматическое определение окружения

Скрипт автоматически определяет, в какой системе он запущен:

- **Termux**: проверяет наличие `$TERMUX_VERSION`
- **Debian/Ubuntu**: проверяет наличие команды `apt`
- **RHEL/CentOS**: проверяет наличие команды `yum`

### Проверка зависимостей

После установки скрипт проверяет:

- ✅ Наличие `ffprobe` в PATH
- ✅ Версии Python и pip
- ✅ Успешность установки Python пакетов

### Безопасность

- Скрипт останавливается при первой ошибке (`set -e`)
- Использует `-y` флаг для неинтерактивной установки
- Не перезаписывает существующий `.env` файл
- На Debian/Ubuntu запрашивает sudo только для системных пакетов

## Устранение неполадок

### Ошибка: "requirements.txt not found"

**Причина**: Скрипт запущен не из корневой директории проекта

**Решение**:
```bash
cd ~/telegram-video-inbox
./scripts/install_dependencies.sh
```

### Ошибка: "ffprobe not found after installation"

**Причина**: ffmpeg установлен неправильно или не в PATH

**Решение** (Termux):
```bash
pkg install ffmpeg
which ffprobe  # Должно вывести путь
```

**Решение** (Debian/Ubuntu):
```bash
sudo apt update
sudo apt install ffmpeg
which ffprobe
```

### Ошибка: "Permission denied"

**Причина**: Скрипт не имеет прав на выполнение

**Решение**:
```bash
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

### Ошибка при установке системных пакетов на Debian/Ubuntu

**Причина**: Нет sudo прав или `apt` заблокирован другим процессом

**Решение**:
```bash
# 1. Убедитесь, что apt не занят
sudo killall apt apt-get

# 2. Обновите списки пакетов
sudo apt update

# 3. Попробуйте снова
./scripts/install_dependencies.sh
```

## Ручная установка (альтернатива)

Если автоматический скрипт не работает, следуйте инструкции в [docs/INSTALLATION.md](INSTALLATION.md) для ручной установки.

## Обновление зависимостей

Для обновления существующих зависимостей:

```bash
cd ~/telegram-video-inbox
git pull  # Обновить код
./scripts/install_dependencies.sh  # Переустановить зависимости
```

Скрипт безопасно обновит пакеты без потери данных или конфигурации.

## Проверка после установки

```bash
# Проверить версии
python --version
pip --version
ffprobe -version

# Проверить Python пакеты
pip list | grep telegram

# Проверить директории
ls -la logs/ tmp/

# Проверить .env
cat .env
```

## Полезные команды

```bash
# Пересоздать виртуальное окружение (опционально)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Переустановить только Python зависимости
pip install --force-reinstall -r requirements.txt

# Проверить конфликты зависимостей
pip check
```

---

**Рекомендация**: Используйте автоматический скрипт для первой установки. Это экономит время и снижает вероятность ошибок конфигурации.
