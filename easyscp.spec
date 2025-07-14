# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['main_packaged.py'],
    pathex=['.'],  # Current directory
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.baked',
        'pyte',
        'easyscp',
        'easyscp.core',
        'easyscp.core.app',
        'easyscp.ui',
        'easyscp.ui.main_window',
        'easyscp.ui.dialogs',
        'easyscp.ui.server_list',
        'easyscp.ui.file_explorer_window',
        'easyscp.ui.terminal_window',
        'easyscp.ui.snippet_dialog',
        'easyscp.ui.settings_dialog',
        'easyscp.ui.design_system',
        'easyscp.ui.base',
        'easyscp.storage',
        'easyscp.storage.server_storage',
        'easyscp.storage.models',
        'easyscp.storage.database',
        'easyscp.storage.db_base',
        'easyscp.storage.db_models',
        'easyscp.connections',
        'easyscp.connections.ssh_connection',
        'easyscp.connections.connection_manager',
        'easyscp.utils',
        'easyscp.utils.logger',
        'easyscp.utils.config',
        'easyscp.utils.helpers',
        'easyscp.utils.db_config',
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
    console=False,  # Set to True if you want a console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)

# For macOS, create an app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='EasySCP.app',
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
        bundle_identifier='com.easyscp.app',
        info_plist={
            'CFBundleName': 'EasySCP',
            'CFBundleDisplayName': 'EasySCP',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': 'True',
        }
    )