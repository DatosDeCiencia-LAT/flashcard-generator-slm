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

REM Write PowerShell script to temp file to avoid line-continuation issues
set PS1=%TEMP%\flashcard_install_python.ps1
(
    echo $ErrorActionPreference = 'Stop'
    echo [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    echo $url = 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe'
    echo $output = "$env:TEMP\python_installer.exe"
    echo Write-Host 'Descargando Python desde python.org...'
    echo ^(New-Object System.Net.WebClient^).DownloadFile^($url, $output^)
    echo Write-Host 'Ejecutando instalador de Python...'
    echo Start-Process $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_test=0' -Wait
    echo Remove-Item $output -Force -ErrorAction SilentlyContinue
) > "%PS1%"

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set PS_EXIT=%errorlevel%
del "%PS1%" 2>nul

if %PS_EXIT% neq 0 (
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

REM Try pre-built wheel for llama-cpp-python first (no compiler needed)
echo Instalando llama-cpp-python (intentando rueda pre-compilada)...
pip install llama-cpp-python==0.3.2 --only-binary :all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu >nul 2>&1
if %errorlevel% neq 0 (
    echo No se encontro rueda pre-compilada. Instalando compilador C++ de Microsoft...
    echo Esto puede tardar 10-20 minutos y requiere ~3 GB de espacio...
    winget install --id Microsoft.VisualStudio.2022.BuildTools --accept-source-agreements --accept-package-agreements --override "--quiet --wait --norestart --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended" 2>nul
    winget install --id Kitware.CMake --accept-source-agreements --accept-package-agreements 2>nul
    echo Compilando llama-cpp-python desde codigo fuente...
    pip install llama-cpp-python==0.3.2 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
    if %errorlevel% neq 0 (
        echo ERROR: No se pudo instalar llama-cpp-python.
        echo Instala manualmente Visual Studio Build Tools desde:
        echo   https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo Selecciona el workload "Desarrollo de escritorio con C++"
        pause
        exit /b 1
    )
)
echo [OK] llama-cpp-python instalado

REM Install remaining dependencies (llama-cpp-python already satisfied)
pip install --prefer-binary -r "%~dp0requirements.txt"
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
