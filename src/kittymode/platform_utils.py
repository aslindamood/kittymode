"""Platform detection and permission utilities for Kitty Mode.

Cats don't discriminate between operating systems - they'll
knock things off ANY desk! Windows, Mac, Linux... all get meows! 🐱💻
"""

import platform
import subprocess
import sys
from typing import Dict


def get_platform() -> str:
    """Return the current platform identifier.
    
    Sniffing out what kind of computer we're lounging on today... *sniff sniff*
    
    Returns:
        'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        return 'linux'


def is_windows() -> bool:
    """Check if running on Windows.
    
    Returns:
        True if on Windows
    """
    return get_platform() == 'windows'


def is_macos() -> bool:
    """Check if running on macOS.
    
    Returns:
        True if on macOS
    """
    return get_platform() == 'macos'


def check_permissions() -> Dict[str, any]:
    """Check if app has required permissions.
    
    Returns:
        Dict with keys:
            - has_permission: bool
            - message: str
            - instructions: str
    """
    if is_macos():
        return _check_macos_accessibility()
    elif is_windows():
        return _check_windows_permissions()
    return {"has_permission": True, "message": "OK", "instructions": ""}


def _check_macos_accessibility() -> Dict[str, any]:
    """Check macOS Accessibility permissions.
    
    Returns:
        Permission status dict
    """
    try:
        # Try to use AppleScript to check System Events access
        # This is a simplified check - real check would use pyobjc
        result = subprocess.run(
            ['osascript', '-e', 
             'tell application "System Events" to get properties'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return {"has_permission": True, "message": "OK", "instructions": ""}
    except FileNotFoundError:
        # osascript not found - not on macOS or path issue
        pass
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass
    
    return {
        "has_permission": False,
        "message": "Accessibility permission required",
        "instructions": """To enable Kitty Mode on macOS:

1. Open System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the left sidebar
3. Click the lock icon to make changes
4. Click "+" and add this application (or Terminal/Python)
5. Restart Kitty Mode

Without this permission, keyboard capture will not work."""
    }


def _check_windows_permissions() -> Dict[str, any]:
    """Check Windows permissions.
    
    Windows usually doesn't need special permissions for keyboard hooks,
    but some antivirus software may flag them.
    
    Returns:
        Permission status dict
    """
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return {
            "has_permission": True,
            "message": "OK" + (" (Administrator)" if is_admin else ""),
            "instructions": ""
        }
    except AttributeError:
        # Not on Windows or windll not available
        return {"has_permission": True, "message": "OK", "instructions": ""}
    except Exception:
        return {"has_permission": True, "message": "OK", "instructions": ""}


def request_permissions() -> None:
    """Open system settings for permission granting."""
    if is_macos():
        try:
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
            ])
        except Exception:
            pass
    elif is_windows():
        # Windows usually doesn't need special permissions
        pass


def get_platform_info() -> Dict[str, str]:
    """Get detailed platform information.
    
    Returns:
        Dict with platform details
    """
    return {
        "platform": get_platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": sys.version,
    }
