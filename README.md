# EasySCP

A modern SSH connection manager with an intuitive GUI, featuring file management, terminal access, and command snippets.

## Features

- **Server Management**: Store and manage multiple SSH server configurations
- **Key Authentication**: Support for PEM and PPK private key files with passphrase protection
- **Secure Storage**: All credentials encrypted using Fernet encryption in SQLite database
- **File Explorer**: Browse, upload, download, create, and delete remote files/folders
- **Terminal Access**: Full terminal emulation with color support
- **Command Snippets**: Save and execute frequently used commands/scripts per server
- **Modern UI**: Clean, minimal black & white interface with consistent design system
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Option 1: Download Pre-built Release (Recommended)

Download the latest release for your platform:

- **Windows**: Download `EasySCP-Windows.zip` or `EasySCP-Setup.exe`
- **macOS**: Download `EasySCP-macOS.dmg`
- **Linux**: Download `EasySCP-Linux.tar.gz`

From the [Releases](https://github.com/yourusername/easyscp/releases) page.

### Option 2: Build from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/easyscp.git
cd easyscp
```

2. Install dependencies:
```bash
brew install python-tk
brew install tcl-tk
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

For building distributables, see [BUILD.md](BUILD.md).

## Project Structure

```
EasySCP/
├── src/
│   └── easyscp/
│       ├── core/           # Core application logic
│       ├── ui/             # UI components with design system
│       ├── connections/    # SSH connection handling
│       ├── storage/        # Encrypted database storage
│       └── utils/          # Utility functions and logging
├── .github/
│   └── workflows/          # GitHub Actions for automated builds
├── logs/                   # Application logs
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── easyscp.spec           # PyInstaller configuration
├── build_*.bat/sh         # Platform-specific build scripts
└── BUILD.md               # Build instructions
```

## Usage

### Adding Servers
1. Click "+ Add" to configure a new server
2. Choose authentication method:
   - **Password**: Enter your SSH password
   - **Private Key**: Browse for PEM/PPK file, optionally add passphrase
3. Save the configuration

### Managing Connections
- **Files**: Opens file explorer for browsing and transferring files
- **Terminal**: Opens terminal with snippet support
- **Snippets**: Click to manage saved commands/scripts for each server
- **Edit/Delete**: Modify or remove server configurations

### File Explorer
- Navigate directories with double-click
- Upload/download files with toolbar buttons
- Create folders, rename, and delete items
- Tip: Click refresh if files don't load initially

### Terminal with Snippets
- Full terminal emulation with color support
- Snippets panel on the right (collapsible)
- Click any snippet to execute instantly
- Supports both single commands and multi-line scripts

### Settings

Access settings through the Settings button or Ctrl+, keyboard shortcut:

- **Appearance**: Theme (dark/light/system) and color scheme
- **Connection**: Default SSH port, timeout, and keepalive settings
- **File Manager**: Show hidden files, default download directory
- **Terminal**: Font family, font size, and buffer size

All settings are saved to the encrypted database automatically.

## Security

- All data stored in encrypted SQLite database
- Server passwords and SSH keys encrypted with Fernet symmetric encryption
- SSH connections use Paramiko library for secure communication
- No passwords or sensitive data stored in plain text
- Database encryption key stored separately

## Database Storage

EasySSH uses SQLite with SQLAlchemy ORM for all data storage:
- **Server Connections**: SSH server configurations with encrypted passwords
- **Settings**: Application preferences and configuration
- **Connection Logs**: History of connections with timestamps

### Migration from JSON

If you have existing `servers.json` or `config.json` files:

```bash
# Migrate servers
python migrate_to_db.py

# Migrate configuration
python migrate_config_to_db.py
```

### Managing Settings

Use the settings manager CLI:

```bash
# List all settings
python manage_settings.py list

# Get a specific setting
python manage_settings.py get appearance.theme

# Change a setting
python manage_settings.py set terminal.font_size 14

# Export/import settings
python manage_settings.py export settings_backup.json
python manage_settings.py import settings_backup.json
```

## Requirements

- Python 3.8+
- paramiko >= 3.0.0
- customtkinter >= 5.0.0
- cryptography >= 41.0.0

## License

MIT License - see LICENSE file for details