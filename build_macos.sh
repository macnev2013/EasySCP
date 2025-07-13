#!/bin/bash

echo "Building EasySCP for macOS..."

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
if [ -d "dist/EasySCP.app" ]; then
    echo ""
    echo "Build successful! App bundle is located at: dist/EasySCP.app"
    echo ""
    
    # Create DMG for distribution
    echo "Creating DMG installer..."
    
    # Create a temporary directory for DMG contents
    mkdir -p dist/dmg
    cp -r dist/EasySCP.app dist/dmg/
    
    # Create Applications symlink
    ln -s /Applications dist/dmg/Applications
    
    # Create DMG
    hdiutil create -volname "EasySCP" -srcfolder dist/dmg -ov -format UDZO dist/EasySCP-macOS.dmg
    
    # Clean up
    rm -rf dist/dmg
    
    echo "DMG installer created: dist/EasySCP-macOS.dmg"
else
    echo ""
    echo "Build failed!"
    exit 1
fi

deactivate