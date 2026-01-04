"""Main bot application entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot.config import config
from bot.middleware.whitelist import WhitelistMiddleware
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
    
    # Create bot session with local API server
    session = AiohttpSession(api=config.bot_api_url)
    
    # Initialize bot
    bot = Bot(
        token=config.bot_token,
        session=session,
        default={"parse_mode": ParseMode.HTML}
    )
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register middleware
    dp.message.middleware(WhitelistMiddleware(logger))
    dp.callback_query.middleware(WhitelistMiddleware(logger))
    logger.info(f"Whitelist enabled for user IDs: {config.allowed_user_ids}")
    
    # Register routers
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    dp.include_router(callbacks.router)
    logger.info("Handlers registered")
    
    # Log bot info
    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        logger.error("Make sure local Bot API server is running!")
        return
    
    # Start polling
    logger.info("Starting long polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise
