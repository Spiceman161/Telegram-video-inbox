# Быстрое тестирование исправления

## Проверка установки ffmpeg

```bash
ffprobe -version
```

Должно вывести версию ffprobe. Если команда не найдена:

```bash
pkg install ffmpeg
```

## Автоматический тест

Запустите тестовый скрипт:

```bash
cd ~/telegram-video-inbox
chmod +x scripts/test_aspect_ratio_fix.sh
./scripts/test_aspect_ratio_fix.sh
```

Скрипт проверит:
1. ✅ Установлен ли ffprobe
2. ✅ Работает ли извлечение метаданных
3. ✅ Показывает размеры видео (width x height)

## Ручное тестирование

### 1. Проверка метаданных

Для любого видео файла:

```bash
ffprobe -v quiet -print_format json -show_streams -select_streams v:0 /path/to/video.mp4
```

Должен вывести JSON с полями `width`, `height`, `duration`.

### 2. Тест в Python

```python
from pathlib import Path
from bot.utils.video_metadata import get_video_metadata

# Укажите путь к тестовому видео
video_path = Path("/storage/emulated/0/Movies/TelegramInbox/test.mp4")

metadata = get_video_metadata(video_path)
if metadata:
    print(f"Width: {metadata['width']}")
    print(f"Height: {metadata['height']}")
    print(f"Duration: {metadata.get('duration')}")
else:
    print("Failed to extract metadata")
```

### 3. Полный workflow тест

1. **Отправьте видео боту** (обычное видео, не document)
2. **Проверьте логи бота**:
   ```bash
   tail -f ~/telegram-video-inbox/logs/bot.log
   ```
   Должна быть запись `upload_received`

3. **Скачайте видео обратно**:
   - Откройте бота в Telegram
   - Нажмите "📥 Inbox"
   - Выберите видео
   - Нажмите "⬇️ Скачать"

4. **Проверьте результат**:
   - Видео должно воспроизводиться с правильным соотношением сторон
   - Не должно быть растяжения по ширине

## Ожидаемые результаты

### ✅ Успешный тест

```
=== Aspect Ratio Fix - Quick Test ===

1. Checking ffprobe installation...
   ✅ ffprobe is installed
   ffprobe version 4.4.2

2. Testing video metadata extraction...
   Testing with: video.mp4
   ✅ Metadata extracted successfully:
      Width: 1920 px
      Height: 1080 px
      Duration: 120.5 sec

   🎉 Aspect ratio fix is working correctly!
   Videos will be sent with correct dimensions: 1920x1080

3. Test complete!
```

### ❌ Проблемы

**Проблема**: `ffprobe: command not found`
- **Решение**: Установите ffmpeg: `pkg install ffmpeg`

**Проблема**: `Failed to extract metadata`
- **Возможные причины**:
  - Файл не является видео
  - Видео повреждено
  - Неподдерживаемый формат
- **Решение**: Попробуйте другой видео файл

**Проблема**: Видео все еще растянуто
- **Проверьте**: Используется ли `SEND_AS=video` в .env
- **Если нет**: Установите `SEND_AS=video` и перезапустите бота
- **Альтернатива**: Используйте `SEND_AS=document` (без preview, но без искажений)

## Отладка

### Проверка логов при отправке

```bash
# Следите за логами при скачивании видео
tail -f ~/telegram-video-inbox/logs/bot.log | grep "file_sent"
```

### Проверка параметров send_video

Добавьте временное логирование в `bot/handlers/callbacks.py`:

```python
if metadata:
    logger.info(f"Sending video with metadata: {metadata}")
    await context.bot.send_video(...)
```

Это покажет, какие метаданные передаются в Telegram API.
