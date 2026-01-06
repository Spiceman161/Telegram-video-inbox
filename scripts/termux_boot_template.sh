#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot startup script for Telegram Video Inbox
# Place this in ~/.termux/boot/

# Acquire wakelock to prevent sleep
termux-wake-lock

# Wait for network to be available
echo "Waiting for network..."
sleep 30

# Start Bot API server in background
echo "Starting Bot API server..."
~/Telegram-video-inbox/scripts/start_bot_api.sh &

# Wait for API server to initialize
sleep 10

# Start bot in background (run as module)
echo "Starting bot..."
cd ~/Telegram-video-inbox && python -m bot.main >> logs/bot-output.log 2>&1 &

echo "Telegram Video Inbox started successfully!"

