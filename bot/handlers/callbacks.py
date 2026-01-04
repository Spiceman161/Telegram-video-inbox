"""Callback query handlers for inline buttons."""

import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery

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


router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("page:"))
async def handle_pagination(callback: CallbackQuery):
    """Handle pagination callbacks."""
    await callback.answer()  # CRITICAL: Answer immediately to remove loading spinner
    
    user_id = callback.from_user.id
    
    # Parse page number
    if callback.data == "page:current":
        return  # Just dismiss the callback
    
    page = int(callback.data.split(":")[1])
    
    # Get files for page
    files, total_files, total_pages = file_manager.list_files(page=page)
    
    # Build message
    if total_files == 0:
        text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
        keyboard = get_empty_list_keyboard()
    else:
        text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
        keyboard = get_file_list_keyboard(files, page, total_pages)
    
    # Update message
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        # Update state
        user_state.update_page(user_id, page)
    except Exception as e:
        logger.error(f"Error updating pagination: {e}")


@router.callback_query(F.data.startswith("file:"))
async def handle_file_selection(callback: CallbackQuery):
    """Handle file selection callback."""
    await callback.answer()
    
    file_id = callback.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    # Build file info message
    text = f"""📹 <b>{file_info.name}</b>

📊 Размер: {file_info.size_human()}
📅 Дата: {file_info.mtime_human()}

Выберите действие:"""
    
    keyboard = get_file_actions_keyboard(file_id)
    
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error showing file actions: {e}")


@router.callback_query(F.data.startswith("download:"))
async def handle_download(callback: CallbackQuery):
    """Handle file download callback."""
    await callback.answer("⬇️ Готовлю файл к отправке...")
    
    user_id = callback.from_user.id
    file_id = callback.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    log_event(
        logger,
        event="file_sent",
        user_id=user_id,
        filename=file_info.name
    )
    
    try:
        # Send file
        if config.send_as == "video":
            await callback.message.answer_video(
                video=file_info.path,
                caption=f"📹 {file_info.name}"
            )
        else:
            await callback.message.answer_document(
                document=file_info.path,
                caption=f"📄 {file_info.name}"
            )
        
        await callback.answer("✅ Файл отправлен!", show_alert=False)
        
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        await callback.answer("❌ Ошибка при отправке файла", show_alert=True)


@router.callback_query(F.data.startswith("delete_ask:"))
async def handle_delete_ask(callback: CallbackQuery):
    """Handle delete confirmation request."""
    await callback.answer()
    
    file_id = callback.data.split(":")[1]
    
    # Get file info
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    text = f"""🗑 <b>Удаление файла</b>

Вы уверены, что хотите удалить:
<code>{file_info.name}</code>

Размер: {file_info.size_human()}

⚠️ <b>Это действие нельзя отменить!</b>"""
    
    keyboard = get_delete_confirmation_keyboard(file_id)
    
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error showing delete confirmation: {e}")


@router.callback_query(F.data.startswith("delete_confirm:"))
async def handle_delete_confirm(callback: CallbackQuery):
    """Handle delete confirmation."""
    user_id = callback.from_user.id
    file_id = callback.data.split(":")[1]
    
    # Get file info before deletion
    file_info = file_manager.get_file_by_id(file_id)
    
    if not file_info:
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    filename = file_info.name
    
    # Delete file
    success = file_manager.delete_file(file_id)
    
    if success:
        log_event(
            logger,
            event="file_deleted",
            user_id=user_id,
            filename=filename
        )
        
        await callback.answer("✅ Файл удалён", show_alert=True)
        
        # Return to file list
        files, total_files, total_pages = file_manager.list_files(page=0)
        
        if total_files == 0:
            text = "📁 <b>Inbox</b>\n\nПапка пуста. Отправьте мне видео!"
            keyboard = get_empty_list_keyboard()
        else:
            text = f"📁 <b>Inbox</b>\n\nВсего файлов: {total_files}\n\nВыберите файл:"
            keyboard = get_file_list_keyboard(files, 0, total_pages)
        
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error returning to list after delete: {e}")
    else:
        await callback.answer("❌ Ошибка при удалении файла", show_alert=True)


@router.callback_query(F.data == "list:refresh")
async def handle_list_refresh(callback: CallbackQuery):
    """Handle list refresh callback."""
    await callback.answer("🔄 Обновляю список...")
    
    user_id = callback.from_user.id
    
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
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        user_state.update_page(user_id, 0)
    except Exception as e:
        logger.error(f"Error refreshing list: {e}")


@router.callback_query(F.data == "list:back")
async def handle_list_back(callback: CallbackQuery):
    """Handle back to list callback."""
    await callback.answer()
    
    user_id = callback.from_user.id
    
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
        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error returning to list: {e}")
