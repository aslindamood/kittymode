"""Entry point for PyInstaller builds.

The front door to the kitty kingdom! Nya~ 🐱🚪
"""
import sys
import os
import io

# Fix for PyInstaller windowed mode: sys.stdout/stderr are None
# which breaks libraries that check sys.stdout.isatty()
# Even silent cats need somewhere to meow! 🐱🤫
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Add src to path so imports work correctly
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    app_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, app_dir)
else:
    # Running as script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(app_dir)
    sys.path.insert(0, src_dir)

# Now import and run
from kittymode.main import main

if __name__ == '__main__':
    main()
