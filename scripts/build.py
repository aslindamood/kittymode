"""Build script for Kitty Mode."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean() -> None:
    """Clean build artifacts."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for d in dirs_to_remove:
        path = Path(d)
        if path.exists():
            shutil.rmtree(path)
            print(f"Removed {d}/")
    
    # Also clean pycache in subdirectories
    for pycache in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache)
        print(f"Removed {pycache}/")


def build_windows() -> None:
    """Build Windows executable."""
    print("Building for Windows...")
    subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'kittymode.spec'
    ], check=True)
    print("\n✓ Build complete: dist/KittyMode.exe")


def build_macos() -> None:
    """Build macOS app bundle."""
    print("Building for macOS...")
    subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'kittymode.spec'
    ], check=True)
    print("\n✓ Build complete: dist/KittyMode.app")


def ensure_icons() -> None:
    """Create icons if they don't exist."""
    if not Path('assets/icon.ico').exists():
        print("Creating icons...")
        subprocess.run([sys.executable, 'scripts/create_icon.py'], check=True)


def main() -> None:
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(description='Build Kitty Mode')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument(
        '--platform', 
        choices=['windows', 'macos', 'auto'], 
        default='auto',
        help='Target platform (default: auto-detect)'
    )
    args = parser.parse_args()
    
    # Ensure we're in project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    if args.clean:
        clean()
        return
    
    # Create icons if needed
    ensure_icons()
    
    # Determine platform
    platform = args.platform
    if platform == 'auto':
        platform = 'windows' if sys.platform == 'win32' else 'macos'
    
    # Build
    if platform == 'windows':
        build_windows()
    else:
        build_macos()


if __name__ == '__main__':
    main()
