"""Video metadata extraction utilities.

This module provides utilities to extract video metadata (width, height, duration)
using ffprobe. This is critical for preserving video aspect ratio when sending
videos through Telegram Bot API.

WHY THIS IS NEEDED:
When sending videos via send_video() without explicit width/height parameters,
Telegram may incorrectly determine the aspect ratio during processing, resulting
in stretched or distorted videos. By extracting and providing the correct metadata,
we ensure the aspect ratio is preserved.

REQUIREMENTS:
- ffmpeg package must be installed (includes ffprobe)
- On Termux: pkg install ffmpeg
- On Debian/Ubuntu: apt install ffmpeg

USAGE:
    from bot.utils.video_metadata import get_video_metadata
    
    metadata = get_video_metadata(video_path)
    if metadata:
        await bot.send_video(
            chat_id=chat_id,
            video=video_path,
            width=metadata['width'],
            height=metadata['height'],
            duration=metadata.get('duration')
        )
"""

import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple


def get_video_metadata(file_path: Path) -> Optional[Dict[str, any]]:
    """
    Extract video metadata using ffprobe.
    
    Args:
        file_path: Path to video file
        
    Returns:
        Dictionary with width, height, duration, or None on error
    """
    try:
        # Use ffprobe to get video metadata
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'v:0',  # Select first video stream
            str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None
        
        data = json.loads(result.stdout)
        
        if not data.get('streams') or len(data['streams']) == 0:
            return None
        
        stream = data['streams'][0]
        
        # Extract metadata
        width = stream.get('width')
        height = stream.get('height')
        
        # Get duration from stream or format
        duration_str = stream.get('duration')
        if duration_str:
            duration = int(float(duration_str))
        else:
            duration = None
        
        # Validate that we have at least width and height
        if width and height:
            return {
                'width': int(width),
                'height': int(height),
                'duration': duration
            }
        
        return None
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, 
            json.JSONDecodeError, ValueError, KeyError):
        return None


def get_video_dimensions(file_path: Path) -> Optional[Tuple[int, int]]:
    """
    Get video dimensions (width, height).
    
    Args:
        file_path: Path to video file
        
    Returns:
        Tuple of (width, height) or None on error
    """
    metadata = get_video_metadata(file_path)
    if metadata:
        return (metadata['width'], metadata['height'])
    return None
