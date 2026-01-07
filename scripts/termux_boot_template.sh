#!/data/data/com.termux/files/usr/bin/bash
# Termux:Boot startup script for Telegram Video Inbox Bot
# Place this in ~/.termux/boot/01-Telegram-video-inbox.sh

# Set full paths
HOME="/data/data/com.termux/files/home"
BIN_DIR="$HOME/.local/bin"
PROJECT_DIR="$HOME/Telegram-video-inbox"
LOG_FILE="$HOME/boot_debug.log"

# Add binaries to PATH
export PATH="$BIN_DIR:$PATH"

echo "$(date): Boot script started" >> "$LOG_FILE"

# Acquire wakelock to prevent sleep
termux-wake-lock

# 1. Wait for system to stabilize and start SSH server
sleep 20
pgrep -x sshd >/dev/null || sshd

# 2. Wait for network to be available
echo "Waiting for network..."
until ping -c 1 8.8.8.8 >/dev/null 2>&1; do 
    sleep 2
done
echo "$(date): Network is ready" >> "$LOG_FILE"

# 3. Clean up temporary files
rm -rf /storage/emulated/0/TelegramVideos/.tmp/* 2>/dev/null

# 4. Start Bot API server
if ! pgrep -x "telegram-bot-api" > /dev/null; then
    echo "$(date): Starting API Server" >> "$LOG_FILE"
    # Use full path to bash and script
    /data/data/com.termux/files/usr/bin/bash "$PROJECT_DIR/scripts/start_bot_api.sh" > "$PROJECT_DIR/logs/bot-api.log" 2>&1 &
    sleep 15
    echo "$(date): Bot API server started" >> "$LOG_FILE"
else
    echo "$(date): Bot API server already running" >> "$LOG_FILE"
fi

# 5. Start the bot
if ! pgrep -f "python -m bot.main" > /dev/null; then
    echo "$(date): Starting Bot" >> "$LOG_FILE"
    cd "$PROJECT_DIR"
    
    # If using venv, uncomment the line below:
    # [ -d "venv" ] && source venv/bin/activate
    
    export PYTHONPATH=$PYTHONPATH:.
    
    # Use nohup to prevent process termination
    nohup python -m bot.main > "$PROJECT_DIR/logs/bot-boot.log" 2>&1 &
    sleep 10
    echo "$(date): Bot started" >> "$LOG_FILE"
else
    echo "$(date): Bot already running" >> "$LOG_FILE"
fi

# 6. Return to home screen
echo "Bot started. Returning to home screen..."
am start -a android.intent.action.MAIN -c android.intent.category.HOME

# Optional: Auto-start video player (example)
# Uncomment below if you want to automatically start VLC player on boot
# sleep 5
# echo "Starting VLC player..."
# am start -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity \
#     -a android.intent.action.VIEW \
#     -d "file:///storage/emulated/0/TelegramVideos" \
#     -t "video/*" \
#     --ez "force_fullscreen" true \
#     --ez "enable_clone_mode" true \
#     --ez "loop" true

echo "$(date): Boot script finished" >> "$LOG_FILE"
