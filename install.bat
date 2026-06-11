@echo off
REM Flashcard Generator - Automatic Installer
REM This script installs Python and all dependencies automatically

echo.
echo ========================================
echo Flashcard Generator - Installation
echo ========================================
echo.

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is already installed
    goto install_deps
)

echo.
echo Step 1: Installing Python (this may take a few minutes)...
echo.

REM Download Python 3.10 installer using PowerShell
PowerShell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    $url = 'https://www.python.org/ftp/python/3.10.13/python-3.10.13-amd64.exe'; ^
    $output = '%TEMP%\python_installer.exe'; ^
    Write-Host 'Downloading Python from official source...'; ^
    (New-Object System.Net.WebClient).DownloadFile($url, $output); ^
    Write-Host 'Running Python installer...'; ^
    & $output /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 | Out-Null; ^
    Remove-Item $output -Force"

if %errorlevel% neq 0 (
    echo.
    echo WARNING: Automatic Python installation failed.
    echo Please visit https://www.python.org/downloads/ and install Python 3.10 manually
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python installed successfully

REM Refresh PATH environment variable
set "PATH=%APPDATA%\Python\Python310\Scripts;C:\Program Files\Python310;%PATH%"

:install_deps
echo.
echo Step 2: Installing required packages...
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Error: Failed to upgrade pip
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ Installation Complete!
echo ========================================
echo.
echo You can now run the app by double-clicking:
echo   run.bat
echo.
pause
