"""Whitelist access control for python-telegram-bot."""

from typing import Optional
from telegram import Update
from telegram.ext import filters

from bot.config import config
from bot.utils.logger import log_event


class WhitelistFilter(filters.MessageFilter):
    """
    Custom filter to check if user is in whitelist.
    
    This filter allows only users from ALLOWED_USER_IDS.
    """
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
    
    def filter(self, message) -> bool:
        """Check if user is in whitelist."""
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        is_allowed = user_id in config.allowed_user_ids
        
        if not is_allowed:
            log_event(
                self.logger,
                event="unauthorized_access",
                user_id=user_id
            )
        
        return is_allowed


def create_whitelist_filter(logger):
    """
    Create a whitelist filter instance.
    
    Args:
        logger: Logger instance for audit logging
        
    Returns:
        WhitelistFilter instance
    """
    return WhitelistFilter(logger)


async def unauthorized_handler(update: Update, context) -> None:
    """
    Handler for unauthorized access attempts.
    
    Sends rejection message to users not in whitelist.
    """
    if update.message:
        await update.message.reply_text("🚫 Доступ запрещён")
    elif update.callback_query:
        await update.callback_query.answer("🚫 Доступ запрещён", show_alert=True)
