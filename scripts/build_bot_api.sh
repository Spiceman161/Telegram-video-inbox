#!/data/data/com.termux/files/usr/bin/bash
# Build Telegram Bot API Server for Termux
# This script automates the compilation of telegram-bot-api

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "  Telegram Bot API Server - Build Script"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if we're in Termux
if [ -z "$TERMUX_VERSION" ]; then
    print_error "This script is designed for Termux environment"
    print_info "If you're on a regular Linux system, adjust the package manager commands"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "─────────────────────────────────────────────────────────"
echo "  Step 1: Installing build dependencies"
echo "─────────────────────────────────────────────────────────"
echo ""

# Install required packages
REQUIRED_PACKAGES="cmake ninja openssl zlib gperf clang wget curl git"

print_info "Installing: $REQUIRED_PACKAGES"

if [ -n "$TERMUX_VERSION" ]; then
    pkg install -y $REQUIRED_PACKAGES
else
    print_info "Please install these packages manually: $REQUIRED_PACKAGES"
    read -p "Press Enter when ready..." 
fi

print_status "Build dependencies installed"
echo ""

# Verify installations
echo "─────────────────────────────────────────────────────────"
echo "  Step 2: Verifying build tools"
echo "─────────────────────────────────────────────────────────"
echo ""

command -v cmake >/dev/null 2>&1 || { print_error "cmake not found"; exit 1; }
command -v ninja >/dev/null 2>&1 || { print_error "ninja not found"; exit 1; }
command -v clang >/dev/null 2>&1 || { print_error "clang not found"; exit 1; }
command -v git >/dev/null 2>&1 || { print_error "git not found"; exit 1; }

print_status "cmake: $(cmake --version | head -n 1)"
print_status "ninja: $(ninja --version)"
print_status "clang: $(clang --version | head -n 1)"
print_status "git: $(git --version)"
echo ""

# Clone telegram-bot-api
echo "─────────────────────────────────────────────────────────"
echo "  Step 3: Cloning telegram-bot-api repository"
echo "─────────────────────────────────────────────────────────"
echo ""

cd ~

if [ -d "telegram-bot-api" ]; then
    print_info "telegram-bot-api directory already exists"
    read -p "Remove and re-clone? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing old directory..."
        rm -rf telegram-bot-api
    else
        print_info "Using existing directory"
        cd telegram-bot-api
        git pull
        cd ..
    fi
fi

if [ ! -d "telegram-bot-api" ]; then
    print_info "Cloning repository (this may take a few minutes)..."
    git clone --recursive https://github.com/tdlib/telegram-bot-api.git
    print_status "Repository cloned"
else
    print_status "Repository ready"
fi

echo ""

# Build
echo "─────────────────────────────────────────────────────────"
echo "  Step 4: Building telegram-bot-api"
echo "─────────────────────────────────────────────────────────"
echo ""

cd ~/telegram-bot-api

# Remove old build directory if exists
if [ -d "build" ]; then
    print_info "Removing old build directory..."
    rm -rf build
fi

mkdir build
cd build

print_info "Configuring build with CMake..."
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX:PATH=.. \
      -GNinja \
      ..

print_status "Configuration complete"
echo ""

print_info "Compiling (this will take 30-60 minutes on weak devices)..."
print_info "Using 2 parallel jobs to avoid overheating..."
echo ""

# Show progress
cmake --build . --target install -j2

print_status "Build complete!"
echo ""

# Verify build
echo "─────────────────────────────────────────────────────────"
echo "  Step 5: Verifying build"
echo "─────────────────────────────────────────────────────────"
echo ""

cd ~/telegram-bot-api

if [ -f "bin/telegram-bot-api" ]; then
    FILE_SIZE=$(ls -lh bin/telegram-bot-api | awk '{print $5}')
    print_status "Binary created: telegram-bot-api ($FILE_SIZE)"
else
    print_error "Build failed: telegram-bot-api binary not found"
    exit 1
fi

# Test executable
if ./bin/telegram-bot-api --help >/dev/null 2>&1; then
    print_status "Binary is executable"
else
    print_error "Binary test failed"
    exit 1
fi

echo ""

# Install to PATH
echo "─────────────────────────────────────────────────────────"
echo "  Step 6: Installing to system PATH"
echo "─────────────────────────────────────────────────────────"
echo ""

mkdir -p ~/.local/bin

if [ -f ~/.local/bin/telegram-bot-api ]; then
    print_info "Removing old installation..."
    rm ~/.local/bin/telegram-bot-api
fi

cp ~/telegram-bot-api/bin/telegram-bot-api ~/.local/bin/
chmod +x ~/.local/bin/telegram-bot-api

print_status "Installed to ~/.local/bin/telegram-bot-api"
echo ""

# Update PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_info "Adding ~/.local/bin to PATH..."
    
    # Detect shell
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    export PATH="$HOME/.local/bin:$PATH"
    
    print_status "PATH updated in $SHELL_RC"
    print_info "You may need to restart your shell or run: source $SHELL_RC"
else
    print_status "PATH already configured"
fi

echo ""

# Final verification
echo "─────────────────────────────────────────────────────────"
echo "  Installation Summary"
echo "─────────────────────────────────────────────────────────"
echo ""

INSTALLED_PATH=$(which telegram-bot-api 2>/dev/null || echo "not in PATH")

if [ "$INSTALLED_PATH" != "not in PATH" ]; then
    print_status "telegram-bot-api is ready to use"
    echo ""
    echo "  Location: $INSTALLED_PATH"
    echo "  Size: $(ls -lh "$INSTALLED_PATH" | awk '{print $5}')"
    echo ""
    print_status "You can now run Bot API server with:"
    echo "    telegram-bot-api --api-id=YOUR_ID --api-hash=YOUR_HASH --local"
else
    print_error "telegram-bot-api not found in PATH"
    echo "  Binary location: ~/.local/bin/telegram-bot-api"
    echo "  Manual PATH setup may be required"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Build completed successfully! 🎉"
echo "═══════════════════════════════════════════════════════════"
echo ""
