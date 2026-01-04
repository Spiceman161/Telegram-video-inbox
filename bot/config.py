"""Configuration management for Telegram Video Inbox bot."""

import os
from pathlib import Path
from typing import List, Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Bot configuration with validation."""

    def __init__(self):
        # Telegram Bot
        self.bot_token = self._get_required("BOT_TOKEN")
        
        # Local Bot API Server
        self.telegram_api_id = self._get_required("TELEGRAM_API_ID")
        self.telegram_api_hash = self._get_required("TELEGRAM_API_HASH")
        self.bot_api_url = os.getenv("BOT_API_URL", "http://localhost:8081")
        
        # Access Control
        allowed_ids = self._get_required("ALLOWED_USER_IDS")
        self.allowed_user_ids = [int(uid.strip()) for uid in allowed_ids.split(",") if uid.strip()]
        
        # File Storage
        self.shared_dir = Path(self._get_required("SHARED_DIR"))
        self.tmp_dir = Path(self._get_required("TMP_DIR"))
        
        # Bot Behavior
        self.page_size = int(os.getenv("PAGE_SIZE", "10"))
        self.max_concurrent_downloads = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))
        self.send_as = os.getenv("SEND_AS", "document")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_path = Path(os.getenv("LOG_PATH", "logs/bot.log"))
        
        # Validate
        self._validate()
    
    def _get_required(self, key: str) -> str:
        """Get required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    def _validate(self):
        """Validate configuration values."""
        if self.page_size < 1 or self.page_size > 50:
            raise ValueError("PAGE_SIZE must be between 1 and 50")
        
        if self.max_concurrent_downloads < 1 or self.max_concurrent_downloads > 5:
            raise ValueError("MAX_CONCURRENT_DOWNLOADS must be between 1 and 5")
        
        if self.send_as not in ["document", "video"]:
            raise ValueError("SEND_AS must be 'document' or 'video'")
        
        if not self.allowed_user_ids:
            raise ValueError("ALLOWED_USER_IDS must contain at least one user ID")

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
