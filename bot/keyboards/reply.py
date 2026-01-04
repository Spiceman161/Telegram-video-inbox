"""Reply keyboard builders."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Get main menu reply keyboard.
    
    Returns:
        Reply keyboard with main menu buttons
    """
    keyboard = [
        [KeyboardButton(text="📥 Inbox")],
        [KeyboardButton(text="⬆️ Статус"), KeyboardButton(text="❓ Помощь")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
