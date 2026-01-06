"""Callback query handlers for inline buttons."""

import logging

from telegram import Update, Message
from telegram.ext import Application, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

from bot.config import config
from bot.services.file_manager import file_manager
from bot.keyboards.inline import (
    get_file_list_keyboard,
    get_file_actions_keyboard,
    get_delete_confirmation_keyboard,
    get_empty_list_keyboard
)
from bot.utils.state import user_state
from bot.utils.logger import log_event
from bot.middleware.whitelist import create_whitelist_filter


async def _safe_edit_or_send(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None,
    parse_mode: str = "HTML"
) -> Message:
    """
    Safely edit message or send new one if it's not the last bot message.
    
    This prevents editing old messages which is confusing for users.
    If the message is not the last one, it will be deleted and a new one sent.
    
    Args:
        update: Update object
        context: Context object
        text: Message text
        reply_markup: Inline keyboard markup
        parse_mode: Parse mode (default HTML)
        
    Returns:
        Message object (edited or new)
    """
    query = update.callback_query
    user_id = update.effective_user.id
    current_msg_id = query.message.message_id
    
    # Check if this is the last live message
    live_msg = user_state.get_live_message(user_id)
    is_last_message = live_msg and live_msg[0] == current_msg_id
    
    if is_last_message:
        # This is the last message, safe to edit
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return query.message
        except BadRequest as e:
            # If edit fails (e.g., message is not modified), fall through to send new
            if "message is not modified" in str(e).lower():
                pass
            else:
                raise
    
    # Not the last message - delete old and send new
    try:
        await query.message.delete()
    except Exception as e:
        # If deletion fails, log but continue
        logging.getLogger(__name__).warning(f"Failed to delete old message: {e}")
    
    # Send new message
    new_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup,
        parse_mode=parse_mode
    )
    
    # Update live message tracking
    page = live_msg[1] if live_msg else 0
    user_state.set_live_message(user_id, new_msg.message_id, page)
    
    return new_msg


async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination callbacks."""
    query = update.callback_query
    await query.answer()  # CRITICAL: Answer immediately to remove loading spinner
    
    user_id = update.effective_user.id
    
    # Parse page number
    if query.data == "page:current":
        return  # Just dismiss the callback
    
    page = int(query.data.split(":")[1])
    
    # Get files for page
    files, total_files, total_pages = file_manager.list_files(page=page)
    
    # Build message
    if total_files == 0:
        text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
        keyboard = get_empty_list_keyboard()
    else:
        text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
        keyboard = get_file_list_keyboard(files, page, total_pages)
    
    # Update message using safe edit
    try:
        await _safe_edit_or_send(
            update=update,
            context=context,
            text=text,
            reply_markup=keyboard
        )
        # Update state
        user_state.update_page(user_id, page)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error updating pagination: {e}")


async def handle_file_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file selection callback."""
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await query.answer("❌ Файл не найден", show_alert=True)
        return
    
    # Build file info message
    text = f"""📹 <b>{file_info.name}</b>

📊 Размер: {file_info.size_human()}
📅 Дата: {file_info.mtime_human()}

Выберите действие:"""
    
    keyboard = get_file_actions_keyboard(file_id)
    
    try:
        await _safe_edit_or_send(
            update=update,
            context=context,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Error showing file actions: {e}")


async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file download callback."""
    query = update.callback_query
    await query.answer("⬇️ Готовлю файл к отправке...")
    
    user_id = update.effective_user.id
    file_id = query.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await query.answer("❌ Файл не найден", show_alert=True)
        return
    
    log_event(
        logging.getLogger(__name__),
        event="file_sent",
        user_id=user_id,
        filename=file_info.name
    )
    
    try:
        # Send file
        if config.send_as == "video":
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=file_info.path,
                caption=f"📹 {file_info.name}"
            )
        else:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=file_info.path,
                caption=f"📄 {file_info.name}"
            )
        
        await query.answer("✅ Файл отправлен!", show_alert=False)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error sending file: {e}")
        await query.answer("❌ Ошибка при отправке файла", show_alert=True)


async def handle_delete_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete confirmation request."""
    query = update.callback_query
    await query.answer()
    
    file_id = query.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await query.answer("❌ Файл не найден", show_alert=True)
        return
    
    text = f"""🗑 <b>Удаление файла</b>

Вы уверены, что хотите удалить:
<code>{file_info.name}</code>

Размер: {file_info.size_human()}

⚠️ <b>Это действие нельзя отменить!</b>"""
    
    keyboard = get_delete_confirmation_keyboard(file_id)
    
    try:
        await _safe_edit_or_send(
            update=update,
            context=context,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Error showing delete confirmation: {e}")


async def handle_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete confirmation."""
    query = update.callback_query
    user_id = update.effective_user.id
    file_id = query.data.split(":")[1]
    
    # Get file info before deletion
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await query.answer("❌ Файл не найден", show_alert=True)
        return
    
    filename = file_info.name
    
    # Delete file
    success = file_manager.delete_file(file_id)
    
    if success:
        log_event(
            logging.getLogger(__name__),
            event="file_deleted",
            user_id=user_id,
            filename=filename
        )
        
        await query.answer("✅ Файл удалён", show_alert=True)
        
        # Return to file list
        files, total_files, total_pages = file_manager.list_files(page=0)
        
        if total_files == 0:
            text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
            keyboard = get_empty_list_keyboard()
        else:
            text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
            keyboard = get_file_list_keyboard(files, 0, total_pages)
        
        try:
            await _safe_edit_or_send(
                update=update,
                context=context,
                text=text,
                reply_markup=keyboard
            )
        except Exception as e:
            logging.getLogger(__name__).error(f"Error returning to list after delete: {e}")
    else:
        await query.answer("❌ Ошибка при удалении файла", show_alert=True)


async def handle_list_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle list refresh callback."""
    query = update.callback_query
    await query.answer("🔄 Обновляю список...")
    
    user_id = update.effective_user.id
    
    # Get files
    files, total_files, total_pages = file_manager.list_files(page=0)
    
    # Build message
    if total_files == 0:
        text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
        keyboard = get_empty_list_keyboard()
    else:
        text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
        keyboard = get_file_list_keyboard(files, 0, total_pages)
    
    try:
        await _safe_edit_or_send(
            update=update,
            context=context,
            text=text,
            reply_markup=keyboard
        )
        user_state.update_page(user_id, 0)
    except Exception as e:
        logging.getLogger(__name__).error(f"Error refreshing list: {e}")


async def handle_list_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to list callback."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get current page or default to 0
    live_msg = user_state.get_live_message(user_id)
    page = live_msg[1] if live_msg else 0
    
    # Get files
    files, total_files, total_pages = file_manager.list_files(page=page)
    
    # Build message
    if total_files == 0:
        text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
        keyboard = get_empty_list_keyboard()
    else:
        text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
        keyboard = get_file_list_keyboard(files, page, total_pages)
    
    try:
        await _safe_edit_or_send(
            update=update,
            context=context,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Error returning to list: {e}")


def register_handlers(app: Application, logger: logging.Logger):
    """
    Register callback query handlers.
    
    Args:
        app: Application instance
        logger: Logger instance
    """
    # Create whitelist filter
    whitelist = create_whitelist_filter(logger)
    
    # Register callback handlers with patterns
    app.add_handler(CallbackQueryHandler(
        handle_pagination,
        pattern="^page:",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_file_selection,
        pattern="^file:",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_download,
        pattern="^download:",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_delete_ask,
        pattern="^delete_ask:",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_delete_confirm,
        pattern="^delete_confirm:",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_list_refresh,
        pattern="^list:refresh$",
        block=False
    ))
    app.add_handler(CallbackQueryHandler(
        handle_list_back,
        pattern="^list:back$",
        block=False
    ))
    
    logger.info("Callback handlers registered")
