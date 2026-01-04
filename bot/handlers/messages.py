"""Message handlers for videos and reply buttons."""

import logging

from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

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
from bot.middleware.whitelist import create_whitelist_filter


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming video messages (native video).
    
    Downloads video to shared directory with atomic write.
    """
    user_id = update.effective_user.id
    video = update.message.video
    
    log_event(
        logging.getLogger(__name__),
        event="upload_received",
        user_id=user_id,
        file_id=video.file_id,
        filename=video.file_name
    )
    
    # Send acknowledgment
    status_msg = await update.message.reply_text("⬇️ Загружаю видео...")
    
    try:
        # Download video
        log_event(
            logging.getLogger(__name__),
            event="download_started",
            user_id=user_id,
            file_id=video.file_id
        )
        
        downloaded_path = await download_manager.download_video(
            bot=context.bot,
            file_id=video.file_id,
            file_unique_id=video.file_unique_id,
            filename=video.file_name,
            mime_type=video.mime_type
        )
        
        if downloaded_path:
            log_event(
                logging.getLogger(__name__),
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
            logging.getLogger(__name__),
            event="download_failed",
            user_id=user_id,
            file_id=video.file_id,
            error=str(e)
        )
        
        await status_msg.edit_text(
            "❌ Ошибка при загрузке видео.\n"
            f"Попробуйте ещё раз."
        )


async def handle_video_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming video files sent as documents.
    
    Downloads video document to shared directory with atomic write.
    """
    user_id = update.effective_user.id
    document = update.message.document
    
    # Additional validation for safety
    if not document.mime_type or not document.mime_type.startswith('video/'):
        # Check file extension as fallback
        if not document.file_name:
            await update.message.reply_text("❌ Поддерживаются только видео файлы")
            return
        
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', '.mpeg', '.mpg']
        if not any(document.file_name.lower().endswith(ext) for ext in video_extensions):
            await update.message.reply_text("❌ Поддерживаются только видео файлы")
            return
    
    log_event(
        logging.getLogger(__name__),
        event="upload_received",
        user_id=user_id,
        file_id=document.file_id,
        filename=document.file_name
    )
    
    # Send acknowledgment
    status_msg = await update.message.reply_text("⬇️ Загружаю видео...")
    
    try:
        # Download video document
        log_event(
            logging.getLogger(__name__),
            event="download_started",
            user_id=user_id,
            file_id=document.file_id
        )
        
        downloaded_path = await download_manager.download_video(
            bot=context.bot,
            file_id=document.file_id,
            file_unique_id=document.file_unique_id,
            filename=document.file_name,
            mime_type=document.mime_type
        )
        
        if downloaded_path:
            log_event(
                logging.getLogger(__name__),
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
            logging.getLogger(__name__),
            event="download_failed",
            user_id=user_id,
            file_id=document.file_id,
            error=str(e)
        )
        
        await status_msg.edit_text(
            "❌ Ошибка при загрузке видео.\n"
            f"Попробуйте ещё раз."
        )


async def handle_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle Inbox button press.
    
    Shows or updates live file list message.
    """
    user_id = update.effective_user.id
    
    log_event(logging.getLogger(__name__), event="list", user_id=user_id)
    
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
            await context.bot.edit_message_text(
                text=text,
                chat_id=update.effective_chat.id,
                message_id=msg_id,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            # Message doesn't exist anymore, create new one
            new_msg = await update.message.reply_html(
                text,
                reply_markup=keyboard
            )
            user_state.set_live_message(user_id, new_msg.message_id, 0)
    else:
        # Create new live message
        new_msg = await update.message.reply_html(
            text,
            reply_markup=keyboard
        )
        user_state.set_live_message(user_id, new_msg.message_id, 0)


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle Status button press.
    
    Shows system status information.
    """
    user_id = update.effective_user.id
    
    status_text = status_service.get_status_message()
    
    await update.message.reply_html(status_text)


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    await update.message.reply_html(help_text)


def register_handlers(app: Application, logger: logging.Logger):
    """
    Register message handlers.
    
    Args:
        app: Application instance
        logger: Logger instance
    """
    # Create whitelist filter
    whitelist = create_whitelist_filter(logger)
    
    # Register video handlers (both native and document)
    app.add_handler(MessageHandler(
        filters.VIDEO & whitelist,
        handle_video
    ))
    app.add_handler(MessageHandler(
        filters.Document.VIDEO & whitelist,
        handle_video_document
    ))
    
    # Register reply button handlers
    app.add_handler(MessageHandler(
        filters.Regex("^📥 Inbox$") & whitelist,
        handle_inbox
    ))
    app.add_handler(MessageHandler(
        filters.Regex("^⬆️ Статус$") & whitelist,
        handle_status
    ))
    app.add_handler(MessageHandler(
        filters.Regex("^❓ Помощь$") & whitelist,
        handle_help
    ))
    
    logger.info("Message handlers registered")
