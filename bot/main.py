"""Main bot application entry point."""

import asyncio
import logging

from telegram import Update
from telegram.ext import Application, ContextTypes, filters

from bot.config import config
from bot.handlers import commands, messages, callbacks
from bot.utils.logger import setup_logger


async def main():
    """Main bot application."""
    # Setup logging
    logger = setup_logger("telegram_video_inbox", config.log_path, config.log_level)
    logger.info("Starting Telegram Video Inbox Bot...")
    
    # Ensure directories exist
    config.ensure_directories()
    logger.info(f"Shared directory: {config.shared_dir}")
    logger.info(f"Temp directory: {config.tmp_dir}")
    
    # Build application with custom Bot API URL
    app = (
        Application.builder()
        .token(config.bot_token)
        .base_url(config.bot_api_url)
        .build()
    )
    
    logger.info(f"Whitelist enabled for user IDs: {config.allowed_user_ids}")
    
    # Register handlers (will be implemented in handler modules)
    commands.register_handlers(app, logger)
    messages.register_handlers(app, logger)
    callbacks.register_handlers(app, logger)
    
    logger.info("Handlers registered")
    
    # Log bot info
    try:
        bot_info = await app.bot.get_me()
        logger.info(f"Bot started: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        logger.error("Make sure local Bot API server is running!")
        return
    
    # Start polling
    logger.info("Starting long polling...")
    try:
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise
