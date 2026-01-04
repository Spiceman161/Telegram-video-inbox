"""Security utilities for path validation and sanitization."""

import os
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove null bytes
    filename = filename.replace('\0', '')
    
    # Replace dangerous characters
    dangerous_chars = ['/', '\\', '..', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    
    return filename


def secure_join(base_dir: Path, filename: str) -> Optional[Path]:
    """
    Safely join base directory with filename, preventing path traversal.
    
    Args:
        base_dir: Base directory path
        filename: Filename to join
        
    Returns:
        Resolved path if safe, None if path traversal detected
    """
    # Sanitize filename first
    safe_filename = sanitize_filename(filename)
    
    # Join paths
    candidate_path = (base_dir / safe_filename).resolve()
    base_dir_resolved = base_dir.resolve()
    
    # Verify the result is within base_dir
    try:
        candidate_path.relative_to(base_dir_resolved)
        return candidate_path
    except ValueError:
        # Path traversal detected
        return None


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """
    Check if target path is safely within base directory.
    
    Args:
        base_dir: Base directory
        target_path: Target path to check
        
    Returns:
        True if safe, False otherwise
    """
    try:
        target_path.resolve().relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False
