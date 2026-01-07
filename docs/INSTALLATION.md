# Installation Guide - Telegram Video Inbox Bot

> **[Русская версия](../README.ru.md)** | **[English](../README.md)**

Complete installation guide for Telegram Video Inbox Bot on Android TV-box in Termux.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Automated Installation (Recommended)](#automated-installation-recommended)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [First Run](#first-run)
6. [Auto-start Setup](#auto-start-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Requirements

- Android TV-box (tested on X96Q, slimBOXtv)
- Android 7.0 or higher
- ARM/ARM64 architecture
- Minimum 2GB RAM (recommended)
- Minimum 5GB free storage
- Internet connection

### Software Requirements

> [!CAUTION]
> **Install Termux from F-Droid ONLY!**
> 
> The Google Play version is outdated and incompatible with add-ons.

**Required:**
- [Termux](https://f-droid.org/packages/com.termux/) from F-Droid
- [Termux:Boot](https://f-droid.org/packages/com.termux.boot/) from F-Droid

### Information to Gather Before Installation

Before starting, collect the following information:

1. **Bot Token** from [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow the wizard
   - Save the token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **API Credentials** from https://my.telegram.org
   - Log in with your phone
   - Go to "API development tools"
   - Create application (App title: `TV-box Video Inbox`, Platform: `Other`)
   - Save **api_id** (number) and **api_hash** (32-character string)

3. **Your Telegram User ID** from [@userinfobot](https://t.me/userinfobot)
   - Send any message
   - Save the user ID number

---

## Automated Installation (Recommended)

The automated installer handles everything: dependencies, Bot API Server compilation, and configuration.

### 1. Disable Battery Optimization

> [!IMPORTANT]
> This is critical for background operation!

1. Open **Settings** → **Apps**
2. Find **Termux** and **Termux:Boot**
3. For each app:
   - Go to **Battery** or **Battery Management**
   - Select **Unrestricted** or **Don't optimize**

### 2. Grant Storage Access

Open Termux and run:

```bash
termux-setup-storage
```

Allow the permission when prompted. This creates `~/storage` with access to `/storage/emulated/0`.

### 3. Clone Repository

```bash
cd ~
git clone https://github.com/Spiceman161/Telegram-video-inbox.git
cd Telegram-video-inbox
```

### 4. Run Installation Script

```bash
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

The script will:
1. Detect your environment
2. Install system packages (Python, Git, ffmpeg, build tools) - **~5 minutes**
3. Build Telegram Bot API Server from source - **~45-60 minutes**
4. Install Python dependencies - **~3 minutes**
5. Create required directories
6. Guide you through configuration (interactive prompts)

> [!NOTE]
> Total time: **~50-70 minutes** depending on your hardware.

### 5. During Installation

You'll be prompted to enter:

```
Enter your Bot Token (from @BotFather):
> 123456789:ABCdefGHIjklMNOpqrsTUVwxyz

Enter your API ID (from my.telegram.org):
> 12345678

Enter your API Hash (from my.telegram.org):
> abcdef1234567890abcdef1234567890

Enter your Telegram User ID (from @userinfobot):
> 123456789

Enter path for video storage [/storage/emulated/0/Movies/TelegramInbox]:
> (press Enter for default)
```

The configuration will be saved to `.env` file.

---

## Manual Installation

For advanced users who prefer manual control.

### 1. Update Termux Packages

```bash
pkg update
pkg upgrade
```

### 2. Install System Dependencies

```bash
# Runtime dependencies
pkg install python git ffmpeg

# Build tools for Bot API Server
pkg install cmake ninja openssl zlib gperf clang wget curl
```

### 3. Build Telegram Bot API Server

```bash
# Use the dedicated build script
chmod +x scripts/build_bot_api.sh
./scripts/build_bot_api.sh
```

Or manually:

```bash
cd ~
git clone --recursive https://github.com/tdlib/telegram-bot-api.git
cd telegram-bot-api

mkdir build
cd build

cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=.. \
      -GNinja \
      ..

cmake --build . --target install -j2

# Install to PATH
mkdir -p ~/.local/bin
cp ~/telegram-bot-api/bin/telegram-bot-api ~/.local/bin/
chmod +x ~/.local/bin/telegram-bot-api

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
which telegram-bot-api
# Should output: /data/data/com.termux/files/home/.local/bin/telegram-bot-api
```

### 4. Install Bot Dependencies

```bash
cd ~/Telegram-video-inbox

# Upgrade pip
python -m pip install --upgrade pip

# Install packages
pip install -r requirements.txt
```

### 5. Create Directories

```bash
mkdir -p logs tmp
mkdir -p ~/telegram-bot-api-data
mkdir -p ~/telegram-bot-api-temp
```

---

## Configuration

### Create .env File

```bash
cp .env.example .env
nano .env  # or vim, or any editor
```

### Required Parameters

```env
# Bot token from @BotFather
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# API credentials from my.telegram.org
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890

# Whitelist (your Telegram user ID from @userinfobot)
ALLOWED_USER_IDS=123456789

# Video storage path (must be accessible by media player)
SHARED_DIR=/storage/emulated/0/Movies/TelegramInbox

# Temporary directory
TMP_DIR=/data/data/com.termux/files/home/Telegram-video-inbox/tmp
```

### Optional Parameters

```env
PAGE_SIZE=10                    # Files per page
MAX_CONCURRENT_DOWNLOADS=2      # Parallel downloads
SEND_AS=video                   # or 'document'
LOG_LEVEL=INFO
LOG_PATH=/data/data/com.termux/files/home/Telegram-video-inbox/logs/bot.log
```

### Create Shared Directory

```bash
mkdir -p /storage/emulated/0/Movies/TelegramInbox
```

---

## First Run

### Migrate Bot to Local Server

> [!CAUTION]
> If your bot previously used cloud API, you must log out first!

```bash
# Replace YOUR_BOT_TOKEN with your actual token
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/logOut"

# Should return: {"ok":true,"result":true}
```

### Start Bot API Server

Open **first** Termux session (or use tmux/screen):

```bash
cd ~/Telegram-video-inbox
./scripts/start_bot_api.sh
```

**Expected output:**

```
Starting Telegram Bot API server...
API ID: 12345678
[Timestamp] [JOB 1] [info] Server started
[Timestamp] [JOB 1] [info] Listening on http://0.0.0.0:8081
```

### Start Bot

Open **second** Termux session:

```bash
cd ~/Telegram-video-inbox
./scripts/start_bot.sh
```

**Expected output:**

```
Starting Telegram Video Inbox Bot...
2026-01-06 12:00:00 | INFO     | Starting Telegram Video Inbox Bot...
2026-01-06 12:00:00 | INFO     | Shared directory: /storage/emulated/0/Movies/TelegramInbox
2026-01-06 12:00:01 | INFO     | Bot started: @your_bot_username (ID: 123456789)
2026-01-06 12:00:01 | INFO     | Starting long polling...
```

### Test the Bot

1. Open Telegram on your phone
2. Find your bot
3. Send `/start` - you should see the welcome message
4. Send a video - it should be saved to your TV-box

---

## Auto-start Setup

### Copy Boot Script

```bash
mkdir -p ~/.termux/boot
cp scripts/termux_boot_template.sh ~/.termux/boot/01-telegram-video-inbox.sh
chmod +x ~/.termux/boot/01-telegram-video-inbox.sh
```

### Activate Termux:Boot

1. Open **Termux:Boot** app at least once
2. This activates it in the system
3. Close the app

### Test Auto-start

```bash
# Reboot device
reboot

# After ~60 seconds, check processes
ps aux | grep telegram

# Should see:
# telegram-bot-api
# python bot/main.py
```

---

## Troubleshooting

### Bot API Server Won't Start

**Symptoms:**
```
[ERROR] Invalid api_id/api_hash
```

**Solution:**
1. Check `.env` file
2. Ensure `TELEGRAM_API_ID` is a number (no quotes)
3. Ensure `TELEGRAM_API_HASH` is 32 characters

### "Failed to get bot info"

**Symptoms:**
```
ERROR | Failed to get bot info
ERROR | Make sure local Bot API server is running!
```

**Solution:**
1. Check Bot API server is running:
   ```bash
   ps aux | grep telegram-bot-api
   ```
2. Check port 8081 is accessible:
   ```bash
   curl http://localhost:8081
   ```
3. Check Bot API server logs:
   ```bash
   tail -f ~/Telegram-video-inbox/logs/bot-api.log
   ```

### Videos Not Saving

**Solution:**
1. Check permissions:
   ```bash
   ls -ld /storage/emulated/0/Movies/TelegramInbox
   ```
2. Try creating a file manually:
   ```bash
   touch /storage/emulated/0/Movies/TelegramInbox/test.txt
   ```
3. Check free space:
   ```bash
   df -h /storage/emulated/0
   ```
4. Check logs:
   ```bash
   grep "download_failed" ~/Telegram-video-inbox/logs/bot.log
   ```

### After Reboot, Bot Doesn't Start

**Solution:**
1. Verify battery optimization is disabled (step 1 of auto-start)
2. Ensure Termux:Boot was opened at least once
3. Check boot script:
   ```bash
   ls -la ~/.termux/boot/
   cat ~/.termux/boot/01-telegram-video-inbox.sh
   ```

### Large File Won't Upload

**Cause:** Possibly using cloud API instead of local.

**Solution:**
1. Verify Bot API server is running with `--local` flag
2. Check `config.bot_api_url` in bot configuration
3. Ensure you ran `logOut` (First Run section)

### "Permission denied" Writing Files

**Solution:**
1. Verify storage permission:
   ```bash
   termux-setup-storage
   ```
2. Try alternative path:
   ```env
   SHARED_DIR=/data/data/com.termux/files/home/storage/shared/Movies/TelegramInbox
   ```

---

## Additional Tips

### Using tmux for Session Management

```bash
# Install tmux
pkg install tmux

# Create session
tmux new -s telegram

# In tmux:
# Ctrl+B then C - new window
# Ctrl+B then N - next window
# Ctrl+B then D - detach

# Reattach
tmux attach -t telegram
```

### Monitoring Resources

```bash
# CPU and memory
top

# Directory size
du -sh /storage/emulated/0/Movies/TelegramInbox
```

### Backup Configuration

```bash
# Backup .env
cp ~/Telegram-video-inbox/.env ~/Telegram-video-inbox/.env.backup
```

### Useful Commands

```bash
# Restart bot (without device reboot)
pkill -f "python bot/main.py"
pkill telegram-bot-api
cd ~/Telegram-video-inbox
./scripts/start_bot_api.sh &
sleep 5
./scripts/start_bot.sh &

# View active processes
ps aux | grep telegram

# Clear logs
> ~/Telegram-video-inbox/logs/bot.log
> ~/Telegram-video-inbox/logs/bot-api.log
```

---

## Done! 🎉

Your Telegram Video Inbox Bot is now set up and ready to use!

For questions or issues, check:
- [README.md](../README.md) - Overview
- [PRD.md](PRD.md) - Project requirements
- GitHub Issues - Report bugs
