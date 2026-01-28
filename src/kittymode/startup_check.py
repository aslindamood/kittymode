"""Startup checks for Kitty Mode.

Making sure the coast is clear before the cat comes out to play! 🐱👀
Gotta check those permissions - even cats need to ask nicely sometimes.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from .platform_utils import check_permissions, request_permissions, get_platform


def run_startup_checks() -> bool:
    """Run startup checks and show dialogs if needed.
    
    *peeks out cautiously* Is it safe to meow? Let's find out!
    
    Returns:
        True if OK to proceed (time to meow!), False if should exit (back to napping)
    """
    perm = check_permissions()
    
    if not perm["has_permission"]:
        # Show permission dialog
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        result = messagebox.askyesno(
            "Kitty Mode - Permission Required",
            f"{perm['message']}\n\n{perm['instructions']}\n\n"
            "Would you like to open System Settings to grant permission?"
        )
        
        if result:
            request_permissions()
            messagebox.showinfo(
                "Kitty Mode",
                "Please grant permission, then restart Kitty Mode."
            )
        
        root.destroy()
        return False
    
    return True


def show_platform_info() -> None:
    """Print platform-specific information."""
    plat = get_platform()
    print(f"Platform: {plat}")
    
    if plat == 'macos':
        print("Note: Accessibility permission required for keyboard capture")
    elif plat == 'windows':
        print("Note: Some antivirus software may flag keyboard hooks")
    elif plat == 'linux':
        print("Note: May require running with elevated privileges on some systems")


def show_startup_error(title: str, message: str) -> None:
    """Show an error dialog at startup.
    
    Args:
        title: Dialog title
        message: Error message
    """
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    except Exception:
        # If tkinter fails, just print to console
        print(f"ERROR: {title}")
        print(message)


def check_dependencies() -> Optional[str]:
    """Check if all required dependencies are installed.
    
    Returns:
        Error message if dependencies missing, None if OK
    """
    missing = []
    
    try:
        import pynput
    except ImportError:
        missing.append("pynput")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import pystray
    except ImportError:
        missing.append("pystray")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    
    if missing:
        return (
            f"Missing required packages: {', '.join(missing)}\n\n"
            f"Please install with:\n"
            f"pip install {' '.join(missing)}"
        )
    
    return None
