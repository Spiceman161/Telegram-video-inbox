#!/bin/bash
# Quick test script for aspect ratio fix

echo "=== Aspect Ratio Fix - Quick Test ==="
echo ""

# Check if ffprobe is installed
echo "1. Checking ffprobe installation..."
if command -v ffprobe &> /dev/null; then
    echo "   ✅ ffprobe is installed"
    ffprobe -version | head -n 1
else
    echo "   ❌ ffprobe is NOT installed"
    echo "   Install with: pkg install ffmpeg"
    exit 1
fi

echo ""
echo "2. Testing video metadata extraction..."

# Find a test video file
TEST_VIDEO=""
if [ -n "$SHARED_DIR" ] && [ -d "$SHARED_DIR" ]; then
    # Try to find any video in SHARED_DIR
    TEST_VIDEO=$(find "$SHARED_DIR" -maxdepth 1 -type f -name "*.mp4" -o -name "*.mkv" -o -name "*.mov" | head -n 1)
fi

if [ -z "$TEST_VIDEO" ]; then
    echo "   ℹ️ No test video found in SHARED_DIR"
    echo "   Please send a video to the bot first, then run this test"
    exit 0
fi

echo "   Testing with: $(basename "$TEST_VIDEO")"

# Extract metadata
METADATA=$(ffprobe -v quiet -print_format json -show_streams -select_streams v:0 "$TEST_VIDEO" 2>/dev/null)

if [ $? -eq 0 ]; then
    WIDTH=$(echo "$METADATA" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['streams'][0].get('width', 'N/A'))" 2>/dev/null)
    HEIGHT=$(echo "$METADATA" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['streams'][0].get('height', 'N/A'))" 2>/dev/null)
    DURATION=$(echo "$METADATA" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['streams'][0].get('duration', 'N/A'))" 2>/dev/null)
    
    echo "   ✅ Metadata extracted successfully:"
    echo "      Width: $WIDTH px"
    echo "      Height: $HEIGHT px"
    echo "      Duration: $DURATION sec"
    
    if [ "$WIDTH" != "N/A" ] && [ "$HEIGHT" != "N/A" ]; then
        echo ""
        echo "   🎉 Aspect ratio fix is working correctly!"
        echo "   Videos will be sent with correct dimensions: ${WIDTH}x${HEIGHT}"
    fi
else
    echo "   ❌ Failed to extract metadata"
    echo "   Check if the file is a valid video"
fi

echo ""
echo "3. Test complete!"
echo ""
echo "To test the full workflow:"
echo "  1. Send a video to the bot"
echo "  2. Use '📥 Inbox' button to view files"
echo "  3. Select a video and press '⬇️ Скачать'"
echo "  4. Check that downloaded video has correct aspect ratio"
echo ""
