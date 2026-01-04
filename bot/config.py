"""Configuration management for Telegram Video Inbox bot."""

from pathlib import Path
from typing import List, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Bot configuration with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Telegram Bot
    bot_token: str = Field(..., description="Bot token from BotFather")
    
    # Local Bot API Server
    telegram_api_id: str = Field(..., description="API ID from my.telegram.org")
    telegram_api_hash: str = Field(..., description="API Hash from my.telegram.org")
    bot_api_url: str = Field(
        default="http://localhost:8081",
        description="Local Bot API server URL"
    )
    
    # Access Control
    allowed_user_ids: List[int] = Field(..., description="Whitelist of Telegram user IDs")
    
    # File Storage
    shared_dir: Path = Field(..., description="Directory for saved videos")
    tmp_dir: Path = Field(..., description="Temporary directory for downloads")
    
    # Bot Behavior
    page_size: int = Field(default=10, ge=1, le=50, description="Files per page")
    max_concurrent_downloads: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum parallel downloads"
    )
    send_as: Literal["document", "video"] = Field(
        default="document",
        description="How to send files back to user"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_path: Path = Field(
        default=Path("logs/bot.log"),
        description="Log file path"
    )

    @field_validator("allowed_user_ids", mode="before")
    @classmethod
    def parse_user_ids(cls, v):
        """Parse comma-separated user IDs from env var."""
        if isinstance(v, str):
            return [int(uid.strip()) for uid in v.split(",") if uid.strip()]
        return v

    @field_validator("shared_dir", "tmp_dir", "log_path", mode="before")
    @classmethod
    def ensure_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
