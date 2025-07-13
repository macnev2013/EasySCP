# Building EasySCP

This document explains how to build EasySCP for Windows, macOS, and Linux.

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Platform-specific requirements:

**Windows:**
- Visual Studio Build Tools or Visual Studio Community (for some Python packages)
- NSIS (optional, for creating installer)

**macOS:**
- Xcode Command Line Tools (`xcode-select --install`)

**Linux:**
- python3-tk and python3-dev packages
- AppImage tools (optional, for creating AppImage)

## Quick Build

### Windows

```batch
build_windows.bat
```

This will create:
- `dist/EasySCP.exe` - Standalone executable
- `dist/EasySCP-Windows.zip` - Compressed distribution

### macOS

```bash
chmod +x build_macos.sh
./build_macos.sh
```

This will create:
- `dist/EasySCP.app` - macOS application bundle
- `dist/EasySCP-macOS.dmg` - DMG installer

### Linux

```bash
chmod +x build_linux.sh
./build_linux.sh
```

This will create:
- `dist/EasySCP` - Linux executable
- `dist/EasySCP-Linux.tar.gz` - Compressed distribution with desktop integration

## Manual Build Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build with PyInstaller:**
   ```bash
   pyinstaller easyscp.spec --clean
   ```

3. **Find your executable:**
   - Windows: `dist/EasySCP.exe`
   - macOS: `dist/EasySCP.app`
   - Linux: `dist/EasySCP`

## Creating Installers

### Windows Installer (NSIS)

1. Install NSIS from https://nsis.sourceforge.io/
2. Build the executable first
3. Run: `makensis installer_windows.nsi`
4. Installer will be created at: `dist/EasySCP-Setup.exe`

### macOS DMG

The build script automatically creates a DMG. To create manually:

```bash
mkdir -p dist/dmg
cp -r dist/EasySCP.app dist/dmg/
ln -s /Applications dist/dmg/Applications
hdiutil create -volname "EasySCP" -srcfolder dist/dmg -ov -format UDZO dist/EasySCP-macOS.dmg
```

### Linux AppImage

1. Download appimagetool:
   ```bash
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   ```

2. Build AppImage:
   ```bash
   ./appimagetool-x86_64.AppImage dist/AppDir dist/EasySCP-x86_64.AppImage
   ```

## Distribution

### File Sizes (Approximate)
- Windows: 40-50 MB
- macOS: 45-55 MB  
- Linux: 45-55 MB

### Recommended Distribution Channels

1. **GitHub Releases** - Automated via GitHub Actions
2. **Website Download** - Host the installers on your website
3. **Package Managers:**
   - Windows: Chocolatey, Scoop
   - macOS: Homebrew
   - Linux: Snap, Flatpak, AUR

## Troubleshooting

### Common Issues

1. **Import errors when running executable:**
   - Add missing modules to `hiddenimports` in `easyscp.spec`

2. **Large file size:**
   - Use UPX compression (already enabled in spec file)
   - Exclude unnecessary packages in spec file

3. **Antivirus false positives:**
   - Sign your executables with a code signing certificate
   - Submit false positive reports to antivirus vendors

4. **macOS Gatekeeper issues:**
   - Sign and notarize your app for distribution
   - Users can right-click and select "Open" to bypass

5. **Linux permission issues:**
   - Make sure to `chmod +x` the executable
   - Include proper desktop integration files

## Code Signing

### Windows
```batch
signtool sign /t http://timestamp.comodoca.com /a dist\EasySCP.exe
```

### macOS
```bash
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/EasySCP.app
```

## Automated Builds

GitHub Actions workflow is configured to automatically build for all platforms when:
- You push a tag starting with 'v' (e.g., v1.0.0)
- You create a pull request
- You manually trigger the workflow

Releases are automatically created with all platform builds when you push a version tag.