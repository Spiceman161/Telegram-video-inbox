"""File management service for video storage operations."""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from bot.config import config
from bot.utils.security import sanitize_filename, is_safe_path


class FileInfo:
    """Information about a file in shared directory."""
    
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.size = path.stat().st_size
        self.mtime = path.stat().st_mtime
        self.file_id = self._generate_file_id()
    
    def _generate_file_id(self) -> str:
        """Generate short file ID from filename."""
        return hashlib.md5(self.name.encode()).hexdigest()[:8]
    
    def size_human(self) -> str:
        """Human-readable file size."""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def mtime_human(self) -> str:
        """Human-readable modification time."""
        dt = datetime.fromtimestamp(self.mtime)
        return dt.strftime('%Y-%m-%d %H:%M')


class FileManager:
    """Manages file operations in shared directory."""
    
    def __init__(self):
        self.shared_dir = config.shared_dir
        self._file_cache: Dict[str, str] = {}  # file_id -> filename
    
    def list_files(self, page: int = 0) -> Tuple[List[FileInfo], int, int]:
        """
        List files in shared directory with pagination.
        
        Args:
            page: Page number (0-indexed)
            
        Returns:
            Tuple of (files_on_page, total_files, total_pages)
        """
        # Get all video files
        all_files = []
        if self.shared_dir.exists():
            for file_path in self.shared_dir.iterdir():
                if file_path.is_file():
                    all_files.append(FileInfo(file_path))
        
        # Sort by modification time (newest first)
        all_files.sort(key=lambda f: f.mtime, reverse=True)
        
        # Update file cache
        self._file_cache.clear()
        for f in all_files:
            self._file_cache[f.file_id] = f.name
        
        # Calculate pagination
        total_files = len(all_files)
        total_pages = (total_files + config.page_size - 1) // config.page_size if total_files > 0 else 1
        
        # Get page slice
        start = page * config.page_size
        end = start + config.page_size
        files_on_page = all_files[start:end]
        
        return files_on_page, total_files, total_pages
    
    def get_file_by_id(self, file_id: str) -> Optional[FileInfo]:
        """
        Get file information by file ID.
        
        Args:
            file_id: Short file ID
            
        Returns:
            FileInfo or None if not found
        """
        filename = self._file_cache.get(file_id)
        if not filename:
            # Rebuild cache and try again
            self.list_files()
            filename = self._file_cache.get(file_id)
        
        if filename:
            file_path = self.shared_dir / filename
            if file_path.exists() and is_safe_path(self.shared_dir, file_path):
                return FileInfo(file_path)
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file by ID with security checks.
        
        Args:
            file_id: Short file ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        file_info = self.get_file_by_id(file_id)
        if not file_info:
            return False
        
        # Security check
        if not is_safe_path(self.shared_dir, file_info.path):
            return False
        
        try:
            file_info.path.unlink()
            # Remove from cache
            self._file_cache.pop(file_id, None)
            return True
        except Exception:
            return False
    
    def generate_filename(
        self,
        original_name: Optional[str],
        file_unique_id: str,
        mime_type: Optional[str] = None
    ) -> str:
        """
        Generate safe filename with collision handling.
        
        Args:
            original_name: Original filename if available
            file_unique_id: Telegram file unique ID
            mime_type: MIME type for extension detection
            
        Returns:
            Safe unique filename
        """
        # Determine base name and extension
        if original_name:
            base_name = sanitize_filename(original_name)
            # Preserve extension
            if '.' in base_name:
                ext = base_name.rsplit('.', 1)[1]
                base_name_no_ext = base_name.rsplit('.', 1)[0]
            else:
                ext = self._extension_from_mime(mime_type)
                base_name_no_ext = base_name
        else:
            # Generate from timestamp and unique ID
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            short_id = file_unique_id[:8]
            ext = self._extension_from_mime(mime_type)
            base_name_no_ext = f"{timestamp}_{short_id}"
        
        # Handle collisions
        filename = f"{base_name_no_ext}.{ext}"
        target_path = self.shared_dir / filename
        
        counter = 1
        while target_path.exists():
            filename = f"{base_name_no_ext} ({counter}).{ext}"
            target_path = self.shared_dir / filename
            counter += 1
        
        return filename
    
    def _extension_from_mime(self, mime_type: Optional[str]) -> str:
        """Get file extension from MIME type."""
        if not mime_type:
            return 'mp4'
        
        mime_map = {
            'video/mp4': 'mp4',
            'video/mpeg': 'mpeg',
            'video/quicktime': 'mov',
            'video/x-msvideo': 'avi',
            'video/x-matroska': 'mkv',
            'video/webm': 'webm',
        }
        
        return mime_map.get(mime_type, 'mp4')
    
    def get_folder_stats(self) -> Dict[str, any]:
        """
        Get folder statistics.
        
        Returns:
            Dictionary with file count and total size
        """
        total_files = 0
        total_size = 0
        
        if self.shared_dir.exists():
            for file_path in self.shared_dir.iterdir():
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
        
        return {
            'total_files': total_files,
            'total_size': total_size
        }


# Global file manager instance
file_manager = FileManager()
