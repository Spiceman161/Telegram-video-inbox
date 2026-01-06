"""Main bot application entry point."""

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes

from bot.config import config
from bot.handlers import commands, messages, callbacks
from bot.utils.logger import setup_logger


def main():
    """Main bot application."""
    # Setup logging
    logger = setup_logger("telegram_video_inbox", config.log_path, config.log_level)
    logger.info("Starting Telegram Video Inbox Bot...")
    
    # Ensure directories exist
    config.ensure_directories()
    logger.info(f"Shared directory: {config.shared_dir}")
    logger.info(f"Temp directory: {config.tmp_dir}")
    
    # Check ffmpeg availability (for video metadata extraction)
    import shutil
    if shutil.which("ffprobe") is None:
        logger.warning("="*60)
        logger.warning("⚠️  ffmpeg/ffprobe is NOT installed!")
        logger.warning("Video aspect ratio preservation may not work correctly.")
        logger.warning("Install with: pkg install ffmpeg (Termux)")
        logger.warning("           or apt install ffmpeg (Debian/Ubuntu)")
        logger.warning("Or run: ./scripts/install_dependencies.sh")
        logger.warning("="*60)
    else:
        logger.info("✓ ffmpeg/ffprobe is available for video metadata extraction")
    
    # Build application with custom Bot API URL
    app = (
        Application.builder()
        .token(config.bot_token)
        .base_url(config.bot_api_url)
        .build()
    )
    
    logger.info(f"Whitelist enabled for user IDs: {config.allowed_user_ids}")
    
    # Register handlers
    commands.register_handlers(app, logger)
    messages.register_handlers(app, logger)
    callbacks.register_handlers(app, logger)
    
    logger.info("Handlers registered")
    
    # Start polling (this will handle the event loop internally)
    logger.info("Starting long polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise

