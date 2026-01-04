"""Whitelist access control middleware."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from bot.config import config
from bot.utils.logger import log_event


class WhitelistMiddleware(BaseMiddleware):
    """
    Middleware to enforce whitelist access control.
    
    Any user not in ALLOWED_USER_IDS is blocked from all operations.
    """
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check if user is in whitelist before processing.
        
        Args:
            handler: Next handler in chain
            event: Telegram event (Message or CallbackQuery)
            data: Handler data
            
        Returns:
            Handler result or None if blocked
        """
        user_id = None
        
        # Extract user_id from different event types
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        # Check whitelist
        if user_id and user_id not in config.allowed_user_ids:
            log_event(
                self.logger,
                event="unauthorized_access",
                user_id=user_id
            )
            
            # Send rejection message
            if isinstance(event, Message):
                await event.answer("🚫 Доступ запрещён")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Доступ запрещён", show_alert=True)
            
            return  # Block further processing
        
        # User is authorized, continue
        return await handler(event, data)
