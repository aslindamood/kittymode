"""Logging configuration for Kitty Mode.

Keeping track of all the meows, mrrrps, and occasional hisses!
Because even cats need to journal sometimes. 📓🐱
"""

import logging
import os
import time
from pathlib import Path
from datetime import datetime

from .platform_utils import is_windows, is_macos


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Set up application logging.
    
    Args:
        level: Logging level for the logger
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('kittymode')
    logger.setLevel(level)
    
    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console)
    
    # File handler
    log_dir = _get_log_dir()
    log_file = log_dir / f"kittymode_{datetime.now().strftime('%Y%m%d')}.log"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)
    
    # Rotate old logs (keep last 7 days)
    _cleanup_old_logs(log_dir, days=7)
    
    return logger


def _get_log_dir() -> Path:
    """Get platform-appropriate log directory.
    
    Returns:
        Path to the log directory
    """
    if is_windows():
        base = Path(os.environ.get('APPDATA', Path.home()))
    elif is_macos():
        base = Path.home() / "Library" / "Logs"
    else:
        base = Path.home() / ".local" / "share"
    
    log_dir = base / "KittyMode" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _cleanup_old_logs(log_dir: Path, days: int = 7) -> None:
    """Remove log files older than specified days.
    
    Args:
        log_dir: Directory containing log files
        days: Number of days to keep logs
    """
    cutoff = time.time() - (days * 86400)
    
    for log_file in log_dir.glob("kittymode_*.log"):
        try:
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
        except OSError:
            pass


# Global logger instance - use DEBUG level to capture diagnostic info
logger = setup_logging(level=logging.DEBUG)
