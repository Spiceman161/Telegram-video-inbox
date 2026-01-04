"""Inline keyboard builders."""

from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.services.file_manager import FileInfo


def get_file_list_keyboard(
    files: List[FileInfo],
    page: int,
    total_pages: int
) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for file list with pagination.
    
    Args:
        files: List of FileInfo objects for current page
        page: Current page number (0-indexed)
        total_pages: Total number of pages
        
    Returns:
        Inline keyboard with file buttons and pagination
    """
    buttons = []
    
    # File buttons
    for file_info in files:
        button_text = f"📹 {file_info.name} ({file_info.size_human()})"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"file:{file_info.file_id}"
            )
        ])
    
    # Pagination row
    if total_pages > 1:
        pagination_row = []
        
        if page > 0:
            pagination_row.append(
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"page:{page-1}")
            )
        
        pagination_row.append(
            InlineKeyboardButton(
                text=f"{page + 1}/{total_pages}",
                callback_data="page:current"
            )
        )
        
        if page < total_pages - 1:
            pagination_row.append(
                InlineKeyboardButton(text="Далее ▶️", callback_data=f"page:{page+1}")
            )
        
        buttons.append(pagination_row)
    
    # Refresh button
    buttons.append([
        InlineKeyboardButton(text="🔄 Обновить", callback_data="list:refresh")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_file_actions_keyboard(file_id: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for file actions.
    
    Args:
        file_id: File ID
        
    Returns:
        Inline keyboard with download/delete buttons
    """
    buttons = [
        [InlineKeyboardButton(text="⬇️ Скачать", callback_data=f"download:{file_id}")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_ask:{file_id}")],
        [InlineKeyboardButton(text="↩️ Назад к списку", callback_data="list:back")]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_delete_confirmation_keyboard(file_id: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for delete confirmation.
    
    Args:
        file_id: File ID
        
    Returns:
        Inline keyboard with confirmation buttons
    """
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"delete_confirm:{file_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data=f"file:{file_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(buttons)


def get_empty_list_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for empty file list.
    
    Returns:
        Inline keyboard with refresh button
    """
    buttons = [
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="list:refresh")]
    ]
    
    return InlineKeyboardMarkup(buttons)
