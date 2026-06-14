@echo off
REM Flashcard Generator - Automatic Installer

REM Auto-elevate to administrator if not already elevated
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    PowerShell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ========================================
echo Flashcard Generator - Instalacion
echo ========================================
echo.

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python ya esta instalado
    goto install_deps
)

echo Paso 1: Instalando Python 3.10 (puede tardar varios minutos)...
echo.

PowerShell -NoProfile -ExecutionPolicy Bypass -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ^
    $url = 'https://www.python.org/ftp/python/3.10.13/python-3.10.13-amd64.exe'; ^
    $output = '%TEMP%\python_installer.exe'; ^
    Write-Host 'Descargando Python desde python.org...'; ^
    (New-Object System.Net.WebClient).DownloadFile($url, $output); ^
    Write-Host 'Ejecutando instalador de Python...'; ^
    Start-Process $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait; ^
    Remove-Item $output -Force"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo instalar Python automaticamente.
    echo Visita https://www.python.org/downloads/ e instala Python 3.10 manualmente.
    echo Durante la instalacion, marca la opcion "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [OK] Python instalado exitosamente

REM Refresh PATH for the current session
set "PATH=C:\Program Files\Python310;C:\Program Files\Python310\Scripts;%PATH%"

:install_deps
echo.
echo Paso 2: Instalando paquetes requeridos...
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ERROR: No se pudo actualizar pip
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Instalacion completada!
echo ========================================
echo.
echo Ahora puedes abrir la app haciendo doble clic en:
echo   run.bat
echo.
pause
