# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

block_cipher = None

# Get the src directory path
src_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'src')

a = Analysis(
    ['main.py'],
    pathex=['.', src_dir],  # Add both current dir and src dir
    binaries=[],
    datas=[
        # Include the entire src directory
        ('src', 'src'),
    ],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'PIL._tkinter_finder',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.baked',
        'pyte',
        'paramiko',
        'cryptography',
        'easyscp',
        'easyscp.core',
        'easyscp.core.app',
        'easyscp.ui',
        'easyscp.storage',
        'easyscp.connections',
        'easyscp.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='EasySCP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)