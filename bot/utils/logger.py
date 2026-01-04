"""Structured logging setup."""

import logging
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_path: Path,
    level: str = "INFO"
) -> logging.Logger:
    """
    Setup structured logger with file and console output.
    
    Args:
        name: Logger name
        log_path: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_event(
    logger: logging.Logger,
    event: str,
    user_id: Optional[int] = None,
    filename: Optional[str] = None,
    file_id: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Log a structured event.
    
    Event types from PRD:
    - upload_received
    - download_started
    - download_ok
    - download_failed
    - list
    - file_sent
    - file_deleted
    - unauthorized_access
    
    Args:
        logger: Logger instance
        event: Event type
        user_id: Telegram user ID
        filename: Filename involved
        file_id: File ID involved
        error: Error message if any
    """
    parts = [f"EVENT={event}"]
    
    if user_id is not None:
        parts.append(f"user_id={user_id}")
    if filename:
        parts.append(f"filename={filename}")
    if file_id:
        parts.append(f"file_id={file_id}")
    if error:
        parts.append(f"error={error}")
    
    message = " | ".join(parts)
    
    if error:
        logger.error(message)
    else:
        logger.info(message)
