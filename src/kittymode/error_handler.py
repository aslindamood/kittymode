"""Error handling utilities for Kitty Mode.

When things go wrong, we land on our feet! Cats always do. 🐱
*hiss* at bugs, *purr* when things work again.
"""

import sys
import traceback
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Optional, TypeVar

from .logger import logger

T = TypeVar('T')


class ErrorHandler:
    """Handles errors and exceptions in Kitty Mode.
    
    Even the most graceful cat knocks things off the table sometimes.
    We're here to clean up the mess! *pushes error off the desk*
    """
    
    @staticmethod
    def handle_exception(exc_type, exc_value, exc_tb) -> None:
        """Global exception handler.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_tb: Exception traceback
        """
        if issubclass(exc_type, KeyboardInterrupt):
            return  # Normal exit
        
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.error(f"Unhandled exception:\n{error_msg}")
        
        # Show user-friendly dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Kitty Mode Error",
                f"An unexpected error occurred:\n\n{exc_value}\n\n"
                "Please check the log file for details."
            )
            root.destroy()
        except Exception:
            pass
    
    @staticmethod
    def safe_call(
        func: Callable[..., T],
        *args,
        default: Optional[T] = None,
        **kwargs
    ) -> Optional[T]:
        """Safely call a function, logging any errors.
        
        Args:
            func: Function to call
            *args: Positional arguments
            default: Default value to return on error
            **kwargs: Keyword arguments
            
        Returns:
            Function result or default value on error
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return default


def install_global_handler() -> None:
    """Install global exception handler."""
    sys.excepthook = ErrorHandler.handle_exception
