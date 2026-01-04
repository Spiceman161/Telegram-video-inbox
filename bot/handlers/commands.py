"""Command handlers."""

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.reply import get_main_menu


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message):
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
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
