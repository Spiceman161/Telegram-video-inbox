"""Message handlers for videos and reply buttons."""

import logging

from aiogram import Router, F
from aiogram.types import Message

from bot.config import config
from bot.services.download_manager import download_manager
from bot.services.file_manager import file_manager
from bot.services.status import status_service
from bot.keyboards.inline import (
    get_file_list_keyboard,
    get_empty_list_keyboard
)
from bot.utils.state import user_state
from bot.utils.logger import log_event


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.video)
async def handle_video(message: Message):
    """
    Handle incoming video messages.
    
    Downloads video to shared directory with atomic write.
    """
    user_id = message.from_user.id
    video = message.video
    
    log_event(
        logger,
        event="upload_received",
        user_id=user_id,
        file_id=video.file_id,
        filename=video.file_name
    )
    
    # Send acknowledgment
    status_msg = await message.answer("⬇️ Загружаю видео...")
    
    try:
        # Download video
        log_event(
            logger,
            event="download_started",
            user_id=user_id,
            file_id=video.file_id
        )
        
        downloaded_path = await download_manager.download_video(
            bot=message.bot,
            file_id=video.file_id,
            file_unique_id=video.file_unique_id,
            filename=video.file_name,
            mime_type=video.mime_type
        )
        
        if downloaded_path:
            log_event(
                logger,
                event="download_ok",
                user_id=user_id,
                filename=downloaded_path.name
            )
            
            await status_msg.edit_text(
                f"✅ Видео сохранено!\n\n"
                f"📁 <code>{downloaded_path.name}</code>",
                parse_mode="HTML"
            )
        else:
            raise Exception("Download returned None")
            
    except Exception as e:
        log_event(
            logger,
            event="download_failed",
            user_id=user_id,
            file_id=video.file_id,
            error=str(e)
        )
        
        await status_msg.edit_text(
            "❌ Ошибка при загрузке видео.\n"
            f"Попробуйте ещё раз."
        )


@router.message(F.text == "📥 Inbox")
async def handle_inbox(message: Message):
    """
    Handle Inbox button press.
    
    Shows or updates live file list message.
    """
    user_id = message.from_user.id
    
    log_event(logger, event="list", user_id=user_id)
    
    # Get files
    files, total_files, total_pages = file_manager.list_files(page=0)
    
    # Build message
    if total_files == 0:
        text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
        keyboard = get_empty_list_keyboard()
    else:
        text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
        keyboard = get_file_list_keyboard(files, 0, total_pages)
    
    # Check if live message exists
    live_msg = user_state.get_live_message(user_id)
    
    if live_msg:
        msg_id, _ = live_msg
        try:
            # Update existing message
            await message.bot.edit_message_text(
                text=text,
                chat_id=message.chat.id,
                message_id=msg_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            # Message doesn't exist anymore, create new one
            new_msg = await message.answer(
                text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            user_state.set_live_message(user_id, new_msg.message_id, 0)
    else:
        # Create new live message
        new_msg = await message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        user_state.set_live_message(user_id, new_msg.message_id, 0)


@router.message(F.text == "⬆️ Статус")
async def handle_status(message: Message):
    """
    Handle Status button press.
    
    Shows system status information.
    """
    user_id = message.from_user.id
    
    status_text = status_service.get_status_message()
    
    await message.answer(status_text, parse_mode="HTML")


@router.message(F.text == "❓ Помощь")
async def handle_help(message: Message):
    """
    Handle Help button press.
    
    Shows help information.
    """
    help_text = """❓ <b>Справка</b>

<b>Отправка видео:</b>
1. Отправьте боту видео файл
2. Бот автоматически сохранит его на TV-box
3. Вы получите подтверждение

<b>Просмотр файлов:</b>
• Нажмите 📥 <b>Inbox</b>
• Появится список всех файлов
• Выберите интересующий файл

<b>Действия с файлами:</b>
• <b>Скачать</b> - получить файл обратно в Telegram
• <b>Удалить</b> - удалить файл с устройства

<b>Статус системы:</b>
• Нажмите ⬆️ <b>Статус</b>
• Увидите свободное место
• Количество файлов
• Активные загрузки

<b>Технические детали:</b>
• Размер файла: без ограничений (локальный API)
• Папка: <code>{}</code>
• Поддерживаемые форматы: все видео форматы

Если возникли вопросы - обратитесь к администратору.""".format(
        config.shared_dir
    )
    
    await message.answer(help_text, parse_mode="HTML")
