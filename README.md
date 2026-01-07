# Telegram Video Inbox Bot

> **[Русская версия](README.ru.md)** | **English**

A Telegram bot for receiving and managing videos on Android TV-box (X96Q, slimBOXtv, and similar devices) using Termux.

## Features

- 📥 **Video Reception**: Send videos to the bot → they're saved to your TV-box
- 📁 **File Management**: Browse, download, and delete files via Telegram
- 🔒 **Whitelist Access**: Only authorized users can access
- ♾️ **No Size Limits**: Uses local Bot API server for unlimited file sizes
- ⚡ **Atomic Writes**: Safe file saving with transaction-like behavior
- 🚀 **Auto-start**: Works with Termux:Boot for automatic startup

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌────────────┐
│   Telegram  │  HTTPS  │   Telegram API   │  HTTP   │  Bot API   │
│   Servers   │◄───────►│     (Cloud)      │◄───────►│   Server   │
└─────────────┘         └──────────────────┘         │  (Local)   │
                                                      └──────┬─────┘
                                                             │ HTTP
                                                      ┌──────▼─────┐
                                                      │  Python    │
                                                      │    Bot     │
                                                      │  (PTB)     │
                                                      └──────┬─────┘
                                                             │
                                                      ┌──────▼─────┐
                                                      │  SHARED_   │
                                                      │    DIR     │
                                                      └────────────┘
```

The entire stack runs locally on your TV-box in Termux.

**Framework:** python-telegram-bot (PTB) - standard Telegram Bot API library for Python, no pydantic-core dependency.

## Requirements

### Hardware
- Android TV-box (X96Q, slimBOXtv, or similar)
- Android 7.0+
- Access to shared storage
- Internet connection

### Software
- **Termux** (from F-Droid - required!)
- **Termux:Boot** (from F-Droid)
- Python 3.8+
- Git
- **ffmpeg** (for correct video metadata handling)

## Quick Start

### Preparation

Before installation, you'll need to gather the following information:

1. **Create a Telegram Bot**
   - Open [@BotFather](https://t.me/BotFather) in Telegram
   - Send `/newbot` and follow instructions
   - Save the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Telegram API Credentials**
   - Visit https://my.telegram.org
   - Log in with your phone number
   - Go to **API development tools**
   - Create a new application:
     - **App title**: `TV-box Video Inbox`
     - **Short name**: `tvbox`
     - **Platform**: `Other`
   - Save the **api_id** (number) and **api_hash** (string)

3. **Get Your Telegram User ID**
   - Open [@userinfobot](https://t.me/userinfobot) in Telegram
   - Send any message
   - Save your **user ID** (number)

4. **Know Your Hardware** (optional, for troubleshooting)
   - Device model (e.g., X96Q, slimBOXtv)
   - Android version

### Installation

> [!IMPORTANT]
> **Install Termux from F-Droid ONLY!**
> 
> The Google Play version is outdated and incompatible.
> - F-Droid: https://f-droid.org/
> - Termux: https://f-droid.org/packages/com.termux/
> - Termux:Boot: https://f-droid.org/packages/com.termux.boot/

**One-Command Installation:**

```bash
# 1. Install Termux from F-Droid, then open it

# 2. Grant storage access
termux-setup-storage
# Allow when prompted

# 3. Clone the repository
cd ~
git clone https://github.com/Spiceman161/Telegram-video-inbox.git
cd Telegram-video-inbox

# 4. Run automated installation
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

The script will:
- Install all system dependencies (Python, Git, ffmpeg, build tools)
- Build Telegram Bot API Server (~45 minutes on TV-box)
- Install Python packages
- Guide you through configuration
- Set up all necessary directories

**During installation**, you'll be asked to enter:
- Bot token (from step 1)
- API ID and API Hash (from step 2)
- Your user ID (from step 3)
- Video storage path (default: `/storage/emulated/0/Movies/TelegramInbox`)

### First Run

After installation completes:

```bash
# If scripts are not executable (automated install handles this)
# Run this only if you get "Permission denied" error:
chmod +x scripts/*.sh

# Start Bot API Server (in first terminal window)
./scripts/start_bot_api.sh &

# Wait 5 seconds for it to initialize
sleep 5

# Start the bot (in second terminal window or use tmux/screen)
./scripts/start_bot.sh &
```

**Test the bot:**
1. Open Telegram on your phone
2. Find your bot
3. Send `/start` - you should see a welcome message
4. Send a video - it should be saved to your TV-box

## Usage

### Bot Commands

- `/start` - Start the bot and show main menu

### Buttons

- **📥 Inbox** - Browse saved files
- **⬆️ Status** - System statistics
- **❓ Help** - Help information

### Sending Videos

Simply send or forward any video to the bot. It will be automatically saved to `SHARED_DIR`.

### Managing Files

1. Press **📥 Inbox**
2. Select a file from the list
3. **⬇️ Download** - Get the file back in Telegram
4. **🗑 Delete** - Delete from disk (with confirmation)

## Auto-start Setup

To make the bot start automatically when your TV-box boots:

```bash
# 1. Install Termux:Boot from F-Droid

# 2. Disable battery optimization
# Settings → Apps → Termux → Battery → Unrestricted
# Settings → Apps → Termux:Boot → Battery → Unrestricted

# 3. Copy boot script
mkdir -p ~/.termux/boot
cp scripts/termux_boot_template.sh ~/.termux/boot/01-telegram-video-inbox.sh
chmod +x ~/.termux/boot/01-telegram-video-inbox.sh

# 4. Open Termux:Boot app at least once

# 5. Reboot your device
```

After reboot, the bot will be ready in ~60 seconds.

## Configuration

All settings are in the `.env` file:

### Required Parameters

```env
# Bot token from @BotFather
BOT_TOKEN=your_bot_token_here

# API credentials from my.telegram.org
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Whitelist (comma-separated Telegram user IDs from @userinfobot)
# You can add multiple users: ALLOWED_USER_IDS=123456789,987654321
ALLOWED_USER_IDS=123456789

# Path to video folder (shared storage)
SHARED_DIR=/storage/emulated/0/Movies/TelegramInbox

# Temporary folder
TMP_DIR=/data/data/com.termux/files/home/Telegram-video-inbox/tmp
```

### Optional Parameters

```env
PAGE_SIZE=10                    # Files per page
MAX_CONCURRENT_DOWNLOADS=2      # Parallel downloads
SEND_AS=video                   # or 'document'
LOG_LEVEL=INFO
```

## Troubleshooting

### Bot doesn't respond

**Diagnostics:**

```bash
# 1. Check if Bot API server is running
ps aux | grep telegram-bot-api

# 2. Check if bot is running  
ps aux | grep "python.*bot.main"

# 3. Check recent logs
tail -50 ~/Telegram-video-inbox/logs/bot.log
tail -50 ~/Telegram-video-inbox/logs/bot-api.log
```

**If bot is not running:**

```bash
cd ~/Telegram-video-inbox
./scripts/start_bot_api.sh &
sleep 5
./scripts/start_bot.sh &
```

### "Failed to get bot info"

**Cause:** Bot API server is not running or unreachable on port 8081.

**Solution:**

```bash
# Check Bot API server logs
tail -50 ~/Telegram-video-inbox/logs/bot-api.log

# Check if port is in use
netstat -tulpn | grep 8081

# Restart Bot API server
pkill telegram-bot-api
./scripts/start_bot_api.sh &
```

### Videos not saving

**Diagnostics:**

```bash
# 1. Check storage permissions
ls -ld /storage/emulated/0/Movies/TelegramInbox

# 2. Check free space
df -h /storage/emulated/0

# 3. Check download errors in logs
grep -i "error\|failed" ~/Telegram-video-inbox/logs/bot.log | tail -20

# 4. Check specific download failures
grep "download_failed" ~/Telegram-video-inbox/logs/bot.log
```

### After reboot, bot doesn't start

**Diagnostics:**

```bash
# 1. Check boot script logs
cat ~/boot_debug.log

# 2. Check if boot script exists and is executable
ls -la ~/.termux/boot/01-Telegram-video-inbox.sh

# 3. Check bot logs from boot
tail -50 ~/Telegram-video-inbox/logs/bot-boot.log
```

**Common issues:**

1. **Battery optimization not disabled**
   - Settings → Apps → Termux → Battery → Unrestricted
   - Settings → Apps → Termux:Boot → Battery → Unrestricted

2. **Termux:Boot not activated**
   - Open Termux:Boot app at least once

3. **Script errors**
   ```bash
   # Test boot script manually
   bash ~/.termux/boot/01-Telegram-video-inbox.sh
   # Check for errors
   ```

4. **PATH issues**
   ```bash
   # Check if telegram-bot-api is in PATH
   which telegram-bot-api
   # Should output: /data/data/com.termux/files/home/.local/bin/telegram-bot-api
   ```

### Checking all logs at once

```bash
# Quick status check
echo "=== Bot Process ===" && ps aux | grep "python.*bot.main" && \
echo "=== API Server ===" && ps aux | grep telegram-bot-api && \
echo "=== Recent Bot Log ===" && tail -10 ~/Telegram-video-inbox/logs/bot.log && \
echo "=== Recent API Log ===" && tail -10 ~/Telegram-video-inbox/logs/bot-api.log
```

### Manual restart

```bash
# Stop everything
pkill -f "python.*bot.main"
pkill telegram-bot-api

# Start fresh
cd ~/Telegram-video-inbox
./scripts/start_bot_api.sh &
sleep 5
./scripts/start_bot.sh &

# Monitor logs
tail -f logs/bot.log
```

## Security

### Whitelist

Only users listed in `ALLOWED_USER_IDS` can:
- Upload files
- Browse file list
- Download and delete files

Others will receive "🚫 Access denied" without information leakage.

### Path Traversal Protection

All paths are validated to prevent directory traversal attacks.

### Logging

All actions are logged with user_id:
- `upload_received` - video received
- `download_ok` - download completed
- `file_sent` - file sent to user
- `file_deleted` - file deleted
- `unauthorized_access` - access attempt denied

Logs: `logs/bot.log`

## Advanced

### Manual Installation

See detailed instructions in [docs/INSTALLATION.md](docs/INSTALLATION.md)

### Using tmux/screen

For easier session management:

```bash
pkg install tmux

# Create session
tmux new -s telegram

# Inside tmux:
# Ctrl+B then C - new window
# Ctrl+B then N - next window
# Ctrl+B then D - detach

# Reattach
tmux attach -t telegram
```

## Contributing

Contributions are welcome! Please see [docs/PRD.md](docs/PRD.md) for project requirements.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created for X96Q/slimBOXtv TV-box deployment.

## Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: See [docs/](docs/) folder for detailed guides
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md) for version history
