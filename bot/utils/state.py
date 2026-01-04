"""User state management for live messages and pagination."""

from typing import Dict, Optional, Tuple


class UserState:
    """In-memory storage for user state."""
    
    def __init__(self):
        # user_id -> (message_id, page)
        self._live_messages: Dict[int, Tuple[int, int]] = {}
    
    def get_live_message(self, user_id: int) -> Optional[Tuple[int, int]]:
        """
        Get live message ID and current page for user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Tuple of (message_id, page) or None if not exists
        """
        return self._live_messages.get(user_id)
    
    def set_live_message(self, user_id: int, message_id: int, page: int = 0):
        """
        Set live message ID and page for user.
        
        Args:
            user_id: Telegram user ID
            message_id: Message ID to track
            page: Current page number (default 0)
        """
        self._live_messages[user_id] = (message_id, page)
    
    def update_page(self, user_id: int, page: int):
        """
        Update current page for user, preserving message ID.
        
        Args:
            user_id: Telegram user ID
            page: New page number
        """
        if user_id in self._live_messages:
            message_id, _ = self._live_messages[user_id]
            self._live_messages[user_id] = (message_id, page)
    
    def clear_user(self, user_id: int):
        """
        Clear state for user.
        
        Args:
            user_id: Telegram user ID
        """
        self._live_messages.pop(user_id, None)


# Global state instance
user_state = UserState()
