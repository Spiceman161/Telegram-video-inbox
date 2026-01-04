"""Download manager with concurrency control."""

import asyncio
import shutil
from pathlib import Path
from typing import Optional

from telegram import Bot

from bot.config import config
from bot.services.file_manager import file_manager


class DownloadManager:
    """Manages video downloads with concurrency control."""
    
    def __init__(self):
        self.semaphore = asyncio.Semaphore(config.max_concurrent_downloads)
        self.active_downloads = 0
    
    async def download_video(
        self,
        bot: Bot,
        file_id: str,
        file_unique_id: str,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Optional[Path]:
        """
        Download video from Telegram with atomic write.
        
        Works for both native video messages and video documents.
        
        Args:
            bot: Bot instance
            file_id: Telegram file ID
            file_unique_id: Telegram unique file ID
            filename: Original filename if available
            mime_type: MIME type
            
        Returns:
            Path to downloaded file or None on error
        """
        async with self.semaphore:
            self.active_downloads += 1
            try:
                return await self._download_impl(
                    bot, file_id, file_unique_id, filename, mime_type
                )
            finally:
                self.active_downloads -= 1
    
    async def _download_impl(
        self,
        bot: Bot,
        file_id: str,
        file_unique_id: str,
        filename: Optional[str],
        mime_type: Optional[str]
    ) -> Optional[Path]:
        """Internal download implementation with atomic write."""
        temp_path = None
        try:
            # Get file info from Telegram
            tg_file = await bot.get_file(file_id)
            
            # Generate safe filename
            final_filename = file_manager.generate_filename(
                filename, file_unique_id, mime_type
            )
            
            # Paths
            final_path = config.shared_dir / final_filename
            temp_path = config.tmp_dir / f"{final_filename}.part"
            
            # Download to temp file
            # PTB's download_to_drive method handles the actual download
            await tg_file.download_to_drive(str(temp_path))
            
            # Atomic move to final location
            # Use shutil.move() instead of rename() to support cross-device moves
            shutil.move(str(temp_path), str(final_path))
            
            return final_path
            
        except Exception as e:
            # Clean up temp file if exists
            if temp_path and temp_path.exists():
                temp_path.unlink()
            raise e
    
    def get_active_count(self) -> int:
        """Get number of active downloads."""
        return self.active_downloads


# Global download manager instance
download_manager = DownloadManager()
