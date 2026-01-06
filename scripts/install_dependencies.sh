#!/data/data/com.termux/files/usr/bin/bash
# Automated installation script for Telegram Video Inbox Bot
# This script performs complete setup from dependencies to Bot API server

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
}

print_section() {
    echo ""
    echo "───────────────────────────────────────────────────────────"
    echo "  $1"
    echo "───────────────────────────────────────────────────────────"
    echo ""
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_question() {
    echo -e "${CYAN}?${NC} $1"
}

# Clear screen and show header
clear
print_header "Telegram Video Inbox Bot - Automated Installer"

echo "This script will:"
echo "  1. Install system dependencies (Python, Git, ffmpeg, build tools)"
echo "  2. Build Telegram Bot API Server"
echo "  3. Install Python dependencies"
echo "  4. Configure the bot"
echo "  5. Set up directories and files"
echo ""
print_info "Total installation time: ~45-90 minutes (depending on hardware)"
echo ""

read -p "Press Enter to continue or Ctrl+C to abort..."

# Detect environment
print_section "Step 1: Environment Detection"

if [ -n "$TERMUX_VERSION" ]; then
    ENVIRONMENT="termux"
    PKG_MANAGER="pkg"
    print_status "Environment: Termux $TERMUX_VERSION"
elif command -v apt &> /dev/null; then
    ENVIRONMENT="debian"
    PKG_MANAGER="apt"
    print_status "Environment: Debian/Ubuntu"
elif command -v yum &> /dev/null; then
    ENVIRONMENT="rhel"
    PKG_MANAGER="yum"
    print_status "Environment: RHEL/CentOS"
else
    print_error "Unknown environment"
    echo "  Please install dependencies manually"
    exit 1
fi

# Hardware info
if [ "$ENVIRONMENT" = "termux" ]; then
    echo ""
    print_info "Hardware Information:"
    echo "  • Architecture: $(uname -m)"
    echo "  • Android Version: $(getprop ro.build.version.release 2>/dev/null || echo 'Unknown')"
    echo "  • Device: $(getprop ro.product.model 2>/dev/null || echo 'Unknown')"
fi

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
print_section "Step 2: Installing System Packages"

if [ "$ENVIRONMENT" = "termux" ]; then
    PACKAGES="python git ffmpeg cmake ninja openssl zlib gperf clang wget curl"
    print_info "Packages to install:"
    echo "  • Python, Git, ffmpeg (runtime)"
    echo "  • cmake, ninja, clang (build tools)"
    echo "  • openssl, zlib, gperf (libraries)"
else
    PACKAGES="python3 python3-pip git ffmpeg cmake ninja-build libssl-dev zlib1g-dev gperf clang wget curl"
    print_info "Packages to install:"
    echo "  • Python3, pip, Git, ffmpeg (runtime)"
    echo "  • cmake, ninja, clang (build tools)"
    echo "  • Development libraries"
fi

echo ""
install_packages "$PACKAGES"

print_status "System packages installed"
echo ""

# Verify critical packages
print_section "Step 3: Verifying Installations"

# Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    print_status "Python: $PYTHON_VERSION"
else
    print_error "Python not found"
    exit 1
fi

# pip
if command -v pip &> /dev/null; then
    PIP_VERSION=$(pip --version 2>&1 | cut -d' ' -f1-2)
    print_status "pip: $PIP_VERSION"
else
    print_error "pip not found"
    exit 1
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_status "Git: $GIT_VERSION"
else
    print_error "Git not found"
    exit 1
fi

# ffmpeg
if command -v ffprobe &> /dev/null; then
    FFPROBE_VERSION=$(ffprobe -version 2>&1 | head -n 1 | cut -d' ' -f1-3)
    print_status "ffprobe: $FFPROBE_VERSION"
else
    print_error "ffprobe not found"
    print_info "ffmpeg is required for correct video metadata handling"
    exit 1
fi

# cmake
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -n 1)
    print_status "cmake: $CMAKE_VERSION"
else
    print_error "cmake not found"
    exit 1
fi

echo ""

# Build Bot API Server
print_section "Step 4: Building Telegram Bot API Server"

# Check if already installed
if command -v telegram-bot-api &> /dev/null; then
    print_status "telegram-bot-api is already installed"
    print_info "Location: $(which telegram-bot-api)"
    echo ""
    read -p "Rebuild anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Skipping Bot API Server build"
        SKIP_BOT_API=1
    else
        SKIP_BOT_API=0
    fi
else
    print_info "telegram-bot-api not found, build required"
    print_info "This step will take 30-60 minutes on TV-box hardware"
    print_info "The process will:"
    echo "  • Clone telegram-bot-api repository"
    echo "  • Compile the server binary"
    echo "  • Install to ~/.local/bin"
    echo ""
    
    read -p "Start Bot API Server build? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Skipping Bot API Server build"
        print_info "You'll need to build it manually later (see docs/INSTALLATION.md)"
        SKIP_BOT_API=1
    else
        SKIP_BOT_API=0
    fi
fi

if [ $SKIP_BOT_API -eq 0 ]; then
    
    # Check if script exists
    if [ -f "scripts/build_bot_api.sh" ]; then
        chmod +x scripts/build_bot_api.sh
        ./scripts/build_bot_api.sh
    else
        print_error "build_bot_api.sh not found"
        print_info "Attempting manual build..."
        
        # Inline build process
        cd ~
        if [ ! -d "telegram-bot-api" ]; then
            print_info "Cloning telegram-bot-api..."
            git clone --recursive https://github.com/tdlib/telegram-bot-api.git
        fi
        
        cd telegram-bot-api
        rm -rf build
        mkdir build
        cd build
        
        print_info "Configuring..."
        cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX:PATH=.. -GNinja ..
        
        print_info "Building..."
        cmake --build . --target install -j2
        
        mkdir -p ~/.local/bin
        cp ~/telegram-bot-api/bin/telegram-bot-api ~/.local/bin/
        chmod +x ~/.local/bin/telegram-bot-api
        
        print_status "Bot API Server built and installed"
    fi
    
    cd ~/Telegram-video-inbox
fi

echo ""

# Create directories early (needed for logs and temp files)
print_info "Creating project directories..."
mkdir -p logs tmp ~/telegram-bot-api-data ~/telegram-bot-api-temp
print_status "Directories created"

echo ""

# Check if we're in the project directory
print_section "Step 5: Setting Up Python Environment"

if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found"
    print_info "Please run this script from the project root directory"
    exit 1
fi

# Upgrade pip (skip in Termux as it's managed by pkg)
if [ "$ENVIRONMENT" != "termux" ]; then
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
else
    print_info "Skipping pip upgrade (managed by Termux pkg)"
fi

# Install Python packages
echo ""
print_info "Installing Python packages..."
pip install -r requirements.txt --quiet

print_status "Python dependencies installed"
echo ""

# Configure .env
print_section "Step 6: Configuration"

if [ -f ".env" ]; then
    print_info ".env file already exists"
    read -p "Overwrite with new configuration? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing .env file"
        CONFIGURE_ENV=0
    else
        CONFIGURE_ENV=1
    fi
else
    CONFIGURE_ENV=1
fi

if [ $CONFIGURE_ENV -eq 1 ]; then
    print_info "Let's configure your bot. You'll need:"
    echo "  1. Bot token from @BotFather"
    echo "  2. API ID and API Hash from https://my.telegram.org"
    echo "  3. Your Telegram User ID (get from @userinfobot)"
    echo ""
    
    # Collect information
    print_question "Enter your Bot Token (from @BotFather):"
    read -r BOT_TOKEN
    
    echo ""
    print_question "Enter your API ID (from my.telegram.org):"
    read -r API_ID
    
    echo ""
    print_question "Enter your API Hash (from my.telegram.org):"
    read -r API_HASH
    
    echo ""
    print_question "Enter your Telegram User ID (from @userinfobot):"
    read -r USER_ID
    
    echo ""
    print_question "Enter path for video storage [/storage/emulated/0/Movies/TelegramInbox]:"
    read -r SHARED_DIR
    SHARED_DIR=${SHARED_DIR:-/storage/emulated/0/Movies/TelegramInbox}
    
    # Create .env file
    cat > .env << EOF
# Bot Configuration
BOT_TOKEN=$BOT_TOKEN

# Telegram API Credentials (from https://my.telegram.org)
TELEGRAM_API_ID=$API_ID
TELEGRAM_API_HASH=$API_HASH

# Access Control (comma-separated user IDs)
ALLOWED_USER_IDS=$USER_ID

# Paths
SHARED_DIR=$SHARED_DIR
TMP_DIR=$(pwd)/tmp

# Optional Settings
PAGE_SIZE=10
MAX_CONCURRENT_DOWNLOADS=2
SEND_AS=video
LOG_LEVEL=INFO
LOG_PATH=$(pwd)/logs/bot.log
EOF
    
    print_status "Configuration saved to .env"
    
    # Create shared directory
    echo ""
    print_info "Creating shared directory..."
    if [ ! -d "$SHARED_DIR" ]; then
        mkdir -p "$SHARED_DIR" 2>/dev/null || {
            print_error "Failed to create $SHARED_DIR"
            print_info "You may need to run: termux-setup-storage"
            print_info "Then create the directory manually"
        }
    fi
    
    if [ -d "$SHARED_DIR" ]; then
        print_status "Shared directory ready: $SHARED_DIR"
    fi
fi

echo ""

# Final steps
print_section "Installation Summary"

print_status "System packages: Installed"
print_status "Python packages: Installed"
print_status "Directories: Created"
print_status "Configuration: $([ $CONFIGURE_ENV -eq 1 ] && echo 'Configured' || echo 'Existing')"

if [ $SKIP_BOT_API -eq 0 ]; then
    if command -v telegram-bot-api &> /dev/null; then
        print_status "Bot API Server: Built and installed"
    else
        print_error "Bot API Server: Build may have failed"
    fi
else
    print_info "Bot API Server: Skipped (manual build required)"
fi

echo ""

# Make scripts executable
print_info "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
print_status "Scripts are ready to use"

echo ""

# Verification
print_section "System Verification"

echo "Python: $(python --version 2>&1)"
echo "pip: $(pip --version 2>&1 | cut -d' ' -f1-2)"
echo "ffprobe: $(ffprobe -version 2>&1 | head -n 1 | cut -d' ' -f1-3)"

if command -v telegram-bot-api &> /dev/null; then
    echo "telegram-bot-api: $(which telegram-bot-api)"
else
    echo "telegram-bot-api: Not in PATH (build may be needed)"
fi

echo ""

# Next steps
print_header "Installation Complete! 🎉"

echo "Next steps:"
echo ""

if [ $SKIP_BOT_API -eq 1 ]; then
    echo "1. Build Bot API Server:"
    echo "   ./scripts/build_bot_api.sh"
    echo ""
    echo "2. Start the bot:"
else
    echo "1. Start the bot:"
fi

echo "   ./scripts/start_bot_api.sh &"
echo "   sleep 5"
echo "   ./scripts/start_bot.sh &"
echo ""

echo "2. Test the bot:"
echo "   • Open Telegram"
echo "   • Send /start to your bot"
echo "   • Send a video to test"
echo ""

echo "3. Set up auto-start (optional):"
echo "   mkdir -p ~/.termux/boot"
echo "   cp scripts/termux_boot_template.sh ~/.termux/boot/01-Telegram-video-inbox.sh"
echo "   chmod +x ~/.termux/boot/01-Telegram-video-inbox.sh"
echo ""

print_info "For detailed documentation, see:"
echo "  • README.md - Overview and quick start"
echo "  • docs/INSTALLATION.md - Detailed installation guide"
echo ""

echo "═══════════════════════════════════════════════════════════"
