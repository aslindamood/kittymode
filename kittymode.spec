# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# Paths
src_path = Path('src')
data_path = Path('data')

# Paths for ONNX model (much smaller than PyTorch)
model_path = Path('models/onnx')

# Data files to include
datas = [
    (str(data_path / 'cat_noises.json'), 'data'),
    (str(data_path / 'embeddings.npy'), 'data'),
    (str(data_path / 'noise_index.json'), 'data'),
    # Bundle the ONNX model for offline use (~90MB vs ~500MB for PyTorch)
    (str(model_path), 'models/onnx'),
]

# Hidden imports for ONNX Runtime
hiddenimports = [
    'onnxruntime',
    'transformers',
    'numpy',
    'tokenizers',
    'pynput.keyboard._win32' if sys.platform == 'win32' else 'pynput.keyboard._darwin',
    'pynput.mouse._win32' if sys.platform == 'win32' else 'pynput.mouse._darwin',
    'PIL._tkinter_finder',
    'kittymode',
    'kittymode.main',
    'kittymode.config',
    'kittymode.logger',
    'kittymode.error_handler',
    'kittymode.keyboard_listener',
    'kittymode.capture_window',
    'kittymode.similarity_search',
    'kittymode.noise_selector',
    'kittymode.text_output',
    'kittymode.toggle',
    'kittymode.tray',
    'kittymode.settings_window',
    'kittymode.platform_utils',
    'kittymode.startup_check',
]

a = Analysis(
    ['src/kittymode/__main__.py'],
    pathex=[str(src_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude PyTorch and related heavy dependencies (not needed with ONNX)
        'torch',
        'torch.cuda',
        'torch.distributed',
        'torchvision',
        'torchaudio',
        'tensorflow',
        'tensorboard',
        'keras',
        'sklearn',
        'scipy',
        'pandas',
        'matplotlib',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KittyMode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else 'assets/icon.icns',
)

# macOS app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='KittyMode.app',
        icon='assets/icon.icns',
        bundle_identifier='com.kittymode.app',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': '1',  # Hide from Dock (tray app)
            'NSAppleEventsUsageDescription': 'Kitty Mode needs accessibility access to capture keyboard input.',
        },
    )
