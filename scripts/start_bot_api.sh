#!/data/data/com.termux/files/usr/bin/bash
# Start Telegram Bot API server in local mode

# Load environment variables
if [ -f ~/telegram-video-inbox/.env ]; then
    export $(grep -v '^#' ~/telegram-video-inbox/.env | xargs)
fi

echo "Starting Telegram Bot API server..."
echo "API ID: $TELEGRAM_API_ID"

# Start Bot API server
telegram-bot-api \
  --api-id="$TELEGRAM_API_ID" \
  --api-hash="$TELEGRAM_API_HASH" \
  --local \
  --http-port=8081 \
  --dir=/data/data/com.termux/files/home/telegram-bot-api-data \
  --temp-dir=/data/data/com.termux/files/home/telegram-bot-api-temp \
  2>&1 | tee ~/telegram-video-inbox/logs/bot-api.log
