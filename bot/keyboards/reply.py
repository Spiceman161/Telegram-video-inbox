"""Reply keyboard builders."""

from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Get main menu reply keyboard.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons
    """
    keyboard = [
        [KeyboardButton("📥 Inbox")],
        [KeyboardButton("⬆️ Статус"), KeyboardButton("❓ Помощь")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
