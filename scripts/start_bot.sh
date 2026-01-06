#!/data/data/com.termux/files/usr/bin/bash
# Start Telegram Video Inbox Bot

echo "Starting Telegram Video Inbox Bot..."

# Navigate to project directory
cd ~/Telegram-video-inbox

# Activate virtual environment if it exists
if [ -d venv ]; then
    source venv/bin/activate
fi

# Start bot (run as module to fix imports)
python -m bot.main 2>&1 | tee -a logs/bot-output.log

