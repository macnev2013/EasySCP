@echo off
echo Building EasySCP for Windows...

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Build executable
echo Building executable...
pyinstaller easyscp_final.spec --clean

REM Check if build was successful
if exist dist\EasySCP.exe (
    echo.
    echo Build successful! Executable is located at: dist\EasySCP.exe
    echo.
    
    REM Create a zip file for distribution
    echo Creating distribution package...
    cd dist
    powershell Compress-Archive -Path EasySCP.exe -DestinationPath EasySCP-Windows.zip -Force
    cd ..
    echo Distribution package created: dist\EasySCP-Windows.zip
) else (
    echo.
    echo Build failed!
    exit /b 1
)

deactivate