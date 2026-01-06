#!/bin/bash
# Automated dependency installation script for Telegram Video Inbox Bot
# This script installs both system packages and Python dependencies

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Telegram Video Inbox Bot - Dependency Installer         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Detect environment
if [ -n "$TERMUX_VERSION" ]; then
    ENVIRONMENT="termux"
    PKG_MANAGER="pkg"
    echo "✓ Detected environment: Termux"
elif command -v apt &> /dev/null; then
    ENVIRONMENT="debian"
    PKG_MANAGER="apt"
    echo "✓ Detected environment: Debian/Ubuntu"
elif command -v yum &> /dev/null; then
    ENVIRONMENT="rhel"
    PKG_MANAGER="yum"
    echo "✓ Detected environment: RHEL/CentOS"
else
    echo "⚠️  Warning: Unknown environment"
    echo "   Please install dependencies manually"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Step 1: Installing system packages"
echo "════════════════════════════════════════════════════════════"
echo ""

# Function to install packages
install_packages() {
    local packages="$1"
    
    if [ "$ENVIRONMENT" = "termux" ]; then
        echo "→ Running: pkg install -y $packages"
        pkg install -y $packages
    elif [ "$ENVIRONMENT" = "debian" ]; then
        echo "→ Running: apt install -y $packages"
        sudo apt update
        sudo apt install -y $packages
    elif [ "$ENVIRONMENT" = "rhel" ]; then
        echo "→ Running: yum install -y $packages"
        sudo yum install -y $packages
    fi
}

# Install system packages
if [ "$ENVIRONMENT" = "termux" ]; then
    PACKAGES="python git ffmpeg"
    echo "📦 Installing: Python, Git, ffmpeg"
    install_packages "$PACKAGES"
else
    PACKAGES="python3 python3-pip git ffmpeg"
    echo "📦 Installing: Python3, pip, Git, ffmpeg"
    install_packages "$PACKAGES"
fi

echo ""
echo "✓ System packages installed successfully"
echo ""

# Verify ffmpeg installation
if command -v ffprobe &> /dev/null; then
    FFPROBE_VERSION=$(ffprobe -version 2>&1 | head -n 1)
    echo "✓ ffprobe installed: $FFPROBE_VERSION"
else
    echo "❌ Error: ffprobe not found after installation"
    echo "   Please install ffmpeg manually"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Step 2: Installing Python dependencies"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if we're in the project directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Upgrade pip
echo "→ Upgrading pip..."
python -m pip install --upgrade pip

# Install Python packages
echo ""
echo "→ Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✓ Python dependencies installed successfully"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  Step 3: Creating required directories"
echo "════════════════════════════════════════════════════════════"
echo ""

# Create directories
mkdir -p logs
mkdir -p tmp

echo "✓ Created: logs/"
echo "✓ Created: tmp/"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Notice: .env file not found"
    if [ -f ".env.example" ]; then
        echo "   Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ Created .env file"
        echo ""
        echo "   ⚠️  IMPORTANT: Edit .env file and fill in your credentials!"
        echo "   Required fields:"
        echo "   - BOT_TOKEN"
        echo "   - TELEGRAM_API_ID"
        echo "   - TELEGRAM_API_HASH"
        echo "   - ALLOWED_USER_IDS"
        echo "   - SHARED_DIR"
        echo "   - TMP_DIR"
    else
        echo "   ⚠️  Warning: .env.example not found"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Installation Summary"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ System packages: Installed"
echo "✅ Python packages: Installed"
echo "✅ Directories: Created"
echo "✅ ffmpeg: Verified"
echo ""

# Verify critical components
echo "Verification:"
echo "  • Python: $(python --version 2>&1)"
echo "  • pip: $(pip --version 2>&1 | cut -d' ' -f1-2)"
echo "  • ffprobe: $(ffprobe -version 2>&1 | head -n 1 | cut -d' ' -f1-3)"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  Next Steps"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ ! -f ".env" ] || ! grep -q "BOT_TOKEN=.*[^=]" .env 2>/dev/null; then
    echo "1. Configure the bot:"
    echo "   nano .env"
    echo "   (Fill in BOT_TOKEN, API credentials, user IDs, paths)"
    echo ""
fi

echo "2. Build Telegram Bot API server (see docs/INSTALLATION.md)"
echo ""
echo "3. Start the bot:"
echo "   ./scripts/start_bot_api.sh &"
echo "   ./scripts/start_bot.sh &"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Installation completed successfully! 🎉                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
