#!/data/data/com.termux/files/usr/bin/bash
# Start Telegram Video Inbox Bot

echo "Starting Telegram Video Inbox Bot..."

# Navigate to project directory
cd ~/telegram-video-inbox

# Activate virtual environment if it exists
if [ -d venv ]; then
    source venv/bin/activate
fi

# Start bot
python bot/main.py 2>&1 | tee -a logs/bot-output.log
