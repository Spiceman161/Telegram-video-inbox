"""System status monitoring service."""

import shutil
from typing import Dict

from bot.config import config
from bot.services.file_manager import file_manager
from bot.services.download_manager import download_manager


class StatusService:
    """Service for system status monitoring."""
    
    def get_disk_space(self) -> Dict[str, int]:
        """
        Get disk space information for shared directory.
        
        Returns:
            Dictionary with total, used, and free space in bytes
        """
        try:
            usage = shutil.disk_usage(config.shared_dir)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free
            }
        except Exception:
            return {'total': 0, 'used': 0, 'free': 0}
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    def get_status_message(self) -> str:
        """
        Generate formatted status message.
        
        Returns:
            Status message text with metrics
        """
        # Disk space
        disk = self.get_disk_space()
        free_space = self.format_bytes(disk['free'])
        total_space = self.format_bytes(disk['total'])
        used_percent = (disk['used'] / disk['total'] * 100) if disk['total'] > 0 else 0
        
        # Folder stats
        stats = file_manager.get_folder_stats()
        total_files = stats['total_files']
        folder_size = self.format_bytes(stats['total_size'])
        
        # Active downloads
        active_dl = download_manager.get_active_count()
        
        message = f"""📊 <b>Статус системы</b>

💾 <b>Диск:</b>
├ Свободно: {free_space} из {total_space}
└ Использовано: {used_percent:.1f}%

📁 <b>Папка TelegramInbox:</b>
├ Файлов: {total_files}
└ Размер: {folder_size}

⬇️ <b>Активных загрузок:</b> {active_dl}

📂 Путь: <code>{config.shared_dir}</code>"""
        
        return message


# Global status service instance
status_service = StatusService()
