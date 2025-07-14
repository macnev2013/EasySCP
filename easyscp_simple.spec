# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all data and binaries from packages
datas = []
binaries = []
hiddenimports = []

# Collect customtkinter
customtkinter_data, customtkinter_binaries, customtkinter_hiddenimports = collect_all('customtkinter')
datas += customtkinter_data
binaries += customtkinter_binaries
hiddenimports += customtkinter_hiddenimports

# Add our package
hiddenimports += [
    'PIL._tkinter_finder',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.ext.baked',
    'pyte',
]

a = Analysis(
    ['main.py'],
    pathex=['.', 'src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add our source code to the bundle
a.datas += [
    ('easyscp/__init__.py', 'src/easyscp/__init__.py', 'DATA'),
    ('easyscp/core/__init__.py', 'src/easyscp/core/__init__.py', 'DATA'),
    ('easyscp/core/app.py', 'src/easyscp/core/app.py', 'DATA'),
    ('easyscp/ui/__init__.py', 'src/easyscp/ui/__init__.py', 'DATA'),
    ('easyscp/ui/main_window.py', 'src/easyscp/ui/main_window.py', 'DATA'),
    ('easyscp/ui/server_list.py', 'src/easyscp/ui/server_list.py', 'DATA'),
    ('easyscp/ui/dialogs.py', 'src/easyscp/ui/dialogs.py', 'DATA'),
    ('easyscp/ui/file_explorer_window.py', 'src/easyscp/ui/file_explorer_window.py', 'DATA'),
    ('easyscp/ui/terminal_window.py', 'src/easyscp/ui/terminal_window.py', 'DATA'),
    ('easyscp/ui/snippet_dialog.py', 'src/easyscp/ui/snippet_dialog.py', 'DATA'),
    ('easyscp/ui/settings_dialog.py', 'src/easyscp/ui/settings_dialog.py', 'DATA'),
    ('easyscp/ui/design_system.py', 'src/easyscp/ui/design_system.py', 'DATA'),
    ('easyscp/ui/base.py', 'src/easyscp/ui/base.py', 'DATA'),
    ('easyscp/storage/__init__.py', 'src/easyscp/storage/__init__.py', 'DATA'),
    ('easyscp/storage/server_storage.py', 'src/easyscp/storage/server_storage.py', 'DATA'),
    ('easyscp/storage/models.py', 'src/easyscp/storage/models.py', 'DATA'),
    ('easyscp/storage/database.py', 'src/easyscp/storage/database.py', 'DATA'),
    ('easyscp/storage/db_base.py', 'src/easyscp/storage/db_base.py', 'DATA'),
    ('easyscp/storage/db_models.py', 'src/easyscp/storage/db_models.py', 'DATA'),
    ('easyscp/connections/__init__.py', 'src/easyscp/connections/__init__.py', 'DATA'),
    ('easyscp/connections/ssh_connection.py', 'src/easyscp/connections/ssh_connection.py', 'DATA'),
    ('easyscp/connections/connection_manager.py', 'src/easyscp/connections/connection_manager.py', 'DATA'),
    ('easyscp/utils/__init__.py', 'src/easyscp/utils/__init__.py', 'DATA'),
    ('easyscp/utils/logger.py', 'src/easyscp/utils/logger.py', 'DATA'),
    ('easyscp/utils/config.py', 'src/easyscp/utils/config.py', 'DATA'),
    ('easyscp/utils/helpers.py', 'src/easyscp/utils/helpers.py', 'DATA'),
    ('easyscp/utils/db_config.py', 'src/easyscp/utils/db_config.py', 'DATA'),
]

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)