"""Command handlers."""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

from bot.keyboards.reply import get_main_menu
from bot.middleware.whitelist import create_whitelist_filter


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    
    Shows welcome message and main menu keyboard.
    """
    welcome_text = """👋 <b>Добро пожаловать в Telegram Video Inbox!</b>

Этот бот позволяет отправлять видео на ваш TV-box и управлять ими.

<b>Как использовать:</b>
• Просто отправьте мне видео - оно сохранится на устройстве
• Нажмите 📥 <b>Inbox</b> - просмотр всех файлов
• Нажмите ⬆️ <b>Статус</b> - информация о системе
• Нажмите ❓ <b>Помощь</b> - справка

<b>Управление файлами:</b>
• Выберите файл из списка
• Скачайте обратно в Telegram
• Удалите ненужные файлы

Готов к работе! 🚀"""
    
    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_menu()
    )


def register_handlers(app: Application, logger: logging.Logger):
    """
    Register command handlers.
    
    Args:
        app: Application instance
        logger: Logger instance
    """
    # Create whitelist filter
    whitelist = create_whitelist_filter(logger)
    
    # Register /start command with whitelist filter
    app.add_handler(CommandHandler("start", cmd_start, filters=whitelist))
    
    logger.info("Command handlers registered")
