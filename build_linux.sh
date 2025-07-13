#!/bin/bash

echo "Building EasySCP for Linux..."

# Clean previous builds
rm -rf build dist __pycache__

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build executable
echo "Building executable..."
pyinstaller easyscp.spec --clean

# Check if build was successful
if [ -f "dist/EasySCP" ]; then
    echo ""
    echo "Build successful! Executable is located at: dist/EasySCP"
    echo ""
    
    # Create AppImage for better distribution
    echo "Creating distribution package..."
    
    # Create directory structure for AppImage
    mkdir -p dist/AppDir/usr/bin
    mkdir -p dist/AppDir/usr/share/applications
    mkdir -p dist/AppDir/usr/share/icons/hicolor/256x256/apps
    
    # Copy executable
    cp dist/EasySCP dist/AppDir/usr/bin/
    
    # Create desktop entry
    cat > dist/AppDir/EasySCP.desktop << EOF
[Desktop Entry]
Type=Application
Name=EasySCP
Comment=SSH Connection Manager
Exec=EasySCP
Icon=easyscp
Categories=Network;RemoteAccess;
Terminal=false
EOF
    
    # Copy desktop entry
    cp dist/AppDir/EasySCP.desktop dist/AppDir/usr/share/applications/
    
    # Create a simple icon if it doesn't exist
    if [ ! -f "assets/icon.png" ]; then
        # Create a placeholder icon using ImageMagick if available
        if command -v convert &> /dev/null; then
            convert -size 256x256 xc:white -fill black -gravity center -pointsize 72 -annotate +0+0 'SCP' dist/AppDir/usr/share/icons/hicolor/256x256/apps/easyscp.png
        fi
    else
        cp assets/icon.png dist/AppDir/usr/share/icons/hicolor/256x256/apps/easyscp.png
    fi
    
    # Make AppRun script
    cat > dist/AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/EasySCP" "$@"
EOF
    
    chmod +x dist/AppDir/AppRun
    
    # Create tar.gz for distribution (AppImage would require additional tools)
    cd dist
    tar -czf EasySCP-Linux.tar.gz AppDir/
    cd ..
    
    echo "Distribution package created: dist/EasySCP-Linux.tar.gz"
    
    # Instructions for AppImage
    echo ""
    echo "To create an AppImage, you can use appimagetool:"
    echo "  wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "  chmod +x appimagetool-x86_64.AppImage"
    echo "  ./appimagetool-x86_64.AppImage dist/AppDir dist/EasySCP-x86_64.AppImage"
else
    echo ""
    echo "Build failed!"
    exit 1
fi

deactivate